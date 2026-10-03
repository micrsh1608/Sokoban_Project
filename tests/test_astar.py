from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/task1"))

from sokoban.core.model import Action
from sokoban.core.parser import load_map
from sokoban.search import astar
from sokoban.search.contracts import SearchLimits, Status, validate_result
from sokoban.search.heuristics import Heuristic


class AStarTests(unittest.TestCase):
    def solve_map(self, name, limits=None):
        layout = load_map(ROOT / "maps/single" / name)
        initial = layout.single_state()
        result = astar.solve(layout.board, initial, limits or SearchLimits())
        validate_result(layout.board, initial, result)
        return result

    def test_tiny_exact_solution(self):
        result = self.solve_map("tiny.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.actions, (Action.EAST,))
        self.assertEqual(result.total_cost, 1)

    def test_two_boxes_matches_ucs_cost(self):
        result = self.solve_map("two_boxes.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.total_cost, 8)

    def test_initial_goal(self):
        result = self.solve_map("already_solved.txt")
        self.assertEqual(result.status, Status.SOLVED)
        self.assertEqual(result.actions, ())
        self.assertEqual(result.total_cost, 0)

    def test_unsolvable(self):
        result = self.solve_map("unsolvable.txt")
        self.assertEqual(result.status, Status.UNSOLVABLE)

    def test_expansion_limit(self):
        result = self.solve_map("two_boxes.txt", SearchLimits(max_expanded=1))
        self.assertEqual(result.status, Status.LIMIT_REACHED)

    def test_timeout(self):
        with patch.object(astar, "perf_counter", side_effect=[100.0, 102.0]):
            result = self.solve_map("tiny.txt", SearchLimits(seconds=1))
        self.assertEqual(result.status, Status.TIMEOUT)


class HeuristicTests(unittest.TestCase):
    def test_not_manhattan_and_goal_zero(self):
        layout = load_map(ROOT / "maps/single/tiny.txt")
        h = Heuristic(layout.board)
        self.assertEqual(h(layout.single_state()), 1.0)
        solved = self.solve_goal(layout)
        self.assertEqual(h(solved), 0.0)

    @staticmethod
    def solve_goal(layout):
        from sokoban.core.rules import step
        return step(layout.board, layout.single_state(), Action.EAST)

    def test_consistency_on_all_tiny_reachable_states(self):
        from sokoban.experiments.verify_heuristic import reachable_states
        from sokoban.core.rules import successors
        layout = load_map(ROOT / "maps/single/tiny.txt")
        h = Heuristic(layout.board)
        states, _, _ = reachable_states(layout.board, layout.single_state(), 72)
        for state in states:
            value = h(state)
            for transition in successors(layout.board, state):
                self.assertLessEqual(value, transition.cost + h(transition.state))


if __name__ == "__main__":
    unittest.main()
