"""Behavioral checks for UCS: optimality, replay, failure and resource limits."""
from collections import deque
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/task1"))
from sokoban.core.model import Action, State
from sokoban.core.parser import load_map, parse_map
from sokoban.core.rules import Transition, is_goal, successors
from sokoban.search import ucs
from sokoban.search.contracts import SearchLimits, Status, validate_result


def bfs_cost(board, initial):
    """Independent FIFO oracle, valid because every Sokoban step costs one."""
    queue = deque([(initial, 0)])
    seen = {initial}
    while queue:
        state, distance = queue.popleft()
        if is_goal(board, state):
            return distance
        for move in successors(board, state):
            if move.state not in seen:
                seen.add(move.state)
                queue.append((move.state, distance + 1))
    return None


class UCSTests(unittest.TestCase):
    def solve_map(self, name, limits=None):
        layout = load_map(ROOT / "maps/single" / name)
        result = ucs.solve(layout.board, layout.single_state(), limits or SearchLimits())
        validate_result(layout.board, layout.single_state(), result)
        return result

    def test_one_push_exact_answer(self):
        result = self.solve_map("tiny.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.actions, (Action.EAST,))
        self.assertEqual(result.total_cost, 1)
        self.assertEqual(result.metrics.expanded, 1)

    def test_initial_goal(self):
        result = self.solve_map("already_solved.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.actions, ())
        self.assertEqual(result.total_cost, 0)
        self.assertEqual(result.metrics.expanded, 0)

    def test_two_boxes_optimal_and_replayable(self):
        result = self.solve_map("two_boxes.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.total_cost, 8)

    def test_exhaustion_is_unsolvable(self):
        result = self.solve_map("unsolvable.txt")
        self.assertEqual(result.status, Status.UNSOLVABLE)
        self.assertIsNone(result.total_cost)

    def test_expansion_limit_is_not_unsolvable(self):
        result = self.solve_map("two_boxes.txt", SearchLimits(max_expanded=1))
        self.assertEqual(result.status, Status.LIMIT_REACHED)
        self.assertEqual(result.metrics.expanded, 1)

    def test_goal_can_be_popped_at_expansion_limit(self):
        result = self.solve_map("tiny.txt", SearchLimits(max_expanded=1))
        self.assertEqual(result.status, Status.SOLVED)

    def test_timeout_with_controlled_clock(self):
        with patch.object(ucs, "perf_counter", side_effect=[100.0, 102.0]):
            result = self.solve_map("tiny.txt", SearchLimits(seconds=1))
        self.assertEqual(result.status, Status.TIMEOUT)
        self.assertEqual(result.actions, ())
        self.assertIsNone(result.total_cost)

    def test_all_72_one_box_states_against_fifo_oracle(self):
        layout = parse_map("%%%%%\n%A  %\n% BD%\n%   %\n%%%%%")
        positions = sorted(layout.board.floors)
        checked = 0
        for player in positions:
            for box in positions:
                if player == box:
                    continue
                state = State(player, frozenset({box}))
                expected = bfs_cost(layout.board, state)
                result = ucs.solve(layout.board, state, SearchLimits())
                with self.subTest(player=player, box=box):
                    self.assertEqual(result.total_cost, expected)
                    self.assertEqual(result.status, Status.UNSOLVABLE if expected is None else Status.SOLVED)
                    validate_result(layout.board, state, result)
                checked += 1
        self.assertEqual(checked, 72)

    def test_improved_path_stale_entry_and_goal_on_pop(self):
        # Weighted synthetic graph exercises cases hidden by unit-cost maps:
        # S->G=20, S->X=5, S->Y=1, Y->X=1, X->G=10. Optimum: 12.
        s, x, y, g = [State((i, 0), frozenset()) for i in range(4)]
        graph = {
            s: [Transition(Action.NORTH, g, 20), Transition(Action.EAST, x, 5), Transition(Action.SOUTH, y, 1)],
            y: [Transition(Action.EAST, x, 1)],
            x: [Transition(Action.NORTH, g, 10)],
            g: [],
        }
        with patch.object(ucs, "successors", side_effect=lambda board, state: iter(graph[state])), \
             patch.object(ucs, "is_goal", side_effect=lambda board, state: state == g):
            result = ucs.solve(None, s, SearchLimits())
        self.assertEqual(result.total_cost, 12)
        self.assertEqual(result.actions, (Action.SOUTH, Action.EAST, Action.NORTH))
        self.assertEqual(result.metrics.expanded, 3)  # stale X=5 was not expanded


if __name__ == "__main__":
    unittest.main()
