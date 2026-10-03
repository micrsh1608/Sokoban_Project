"""A* and heuristic checks independent of GUI and timing benchmarks."""
from pathlib import Path
import sys
from threading import Event
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source/task1'))
from sokoban.core.model import State
from sokoban.core.parser import load_map, parse_map
from sokoban.core.rules import successors
from sokoban.search import astar, ucs
from sokoban.search.contracts import SearchLimits, Status, validate_result
from sokoban.search.heuristics import Heuristic
from sokoban.experiments.verify_heuristic import verify_map
from test_ucs import bfs_cost


class AStarTests(unittest.TestCase):
    def test_all_72_states_optimal_and_heuristic_consistent(self):
        layout = parse_map('%%%%%\n%A  %\n% BD%\n%   %\n%%%%%')
        board = layout.board
        h = Heuristic(board)
        for player in board.floors:
            for box in board.floors - {player}:
                state = State(player, frozenset({box}))
                with self.subTest(player=player, box=box):
                    expected = bfs_cost(board, state)
                    result = astar.solve(board, state, SearchLimits())
                    self.assertEqual(result.total_cost, expected)
                    self.assertEqual(result.status, Status.UNSOLVABLE if expected is None else Status.SOLVED)
                    validate_result(board, state, result)
                    self.assertGreaterEqual(h(state), 0)
                    if expected is not None:
                        self.assertLessEqual(h(state), expected)
                    for move in successors(board, state):
                        self.assertLessEqual(h(state), move.cost + h(move.state))

    def test_map_costs_and_replay(self):
        for name, cost in [('tiny', 1), ('two_boxes', 8), ('already_solved', 0)]:
            with self.subTest(map=name):
                layout = load_map(ROOT / f'maps/single/{name}.txt')
                result = astar.solve(layout.board, layout.single_state(), SearchLimits())
                self.assertEqual(result.total_cost, cost)
                validate_result(layout.board, layout.single_state(), result)

    def test_limits_are_not_unsolvable(self):
        layout = load_map(ROOT / 'maps/single/two_boxes.txt')
        result = astar.solve(layout.board, layout.single_state(), SearchLimits(max_expanded=1))
        self.assertEqual(result.status, Status.LIMIT_REACHED)
        with patch.object(astar, 'perf_counter', side_effect=[0, 2]):
            result = astar.solve(layout.board, layout.single_state(), SearchLimits(seconds=1))
        self.assertEqual(result.status, Status.TIMEOUT)

    def test_solver_cancellation(self):
        layout = load_map(ROOT / 'maps/single/two_boxes.txt')
        event = Event()
        event.set()
        for solver in (ucs.solve, astar.solve):
            result = solver(layout.board, layout.single_state(), SearchLimits(), cancel_event=event)
            self.assertEqual(result.status, Status.CANCELLED)
            validate_result(layout.board, layout.single_state(), result)

    def test_empty_box_iterator(self):
        layout = load_map(ROOT / 'maps/single/tiny.txt')
        self.assertEqual(Heuristic(layout.board).minimum_push_distance(iter(())), 0)

    def test_sample_verification(self):
        layout = load_map(ROOT / 'maps/single/two_boxes.txt')
        report = verify_map(layout.board, layout.single_state(), Heuristic(layout.board), max_states=50)
        self.assertEqual(report['status'], 'sample_passed')
        self.assertEqual(report['violations'], [])
        self.assertEqual(report['consistency_states_checked'], 50)
        self.assertGreater(report['states_checked'], 0)

    def test_unsolvable_sample_is_inconclusive(self):
        layout = load_map(ROOT / 'maps/single/unsolvable.txt')
        report = verify_map(layout.board, layout.single_state(), Heuristic(layout.board))
        self.assertEqual(report['status'], 'inconclusive')
        self.assertFalse(report['admissibility_has_evidence'])
        self.assertGreater(report['consistency_states_checked'], 0)
