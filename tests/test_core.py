from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/task1"))
from sokoban.core.model import Action, State
from sokoban.core.parser import load_map, parse_map
from sokoban.core.rules import is_goal, replay, step
from sokoban.core.history import History
from sokoban.search.contracts import SearchResult, Status, validate_result
from sokoban.competitive.engine import CompetitionEngine


class CoreTests(unittest.TestCase):
    def test_tiny_solution(self):
        layout = load_map(ROOT / "maps/single/tiny.txt")
        initial = layout.single_state()
        solved = step(layout.board, initial, Action.EAST)
        self.assertTrue(is_goal(layout.board, solved))
        validate_result(layout.board, initial, SearchResult(Status.SOLVED, (Action.EAST,), 1))

    def test_c_keeps_goal_after_push(self):
        layout = parse_map("%%%%%%\n%AC  %\n%%%%%%")
        pushed = step(layout.board, layout.single_state(), Action.EAST)
        self.assertIn((1, 2), layout.board.goals)
        self.assertNotIn((1, 2), pushed.boxes)
        self.assertIn((1, 3), pushed.boxes)

    def test_cannot_push_two_boxes(self):
        layout = parse_map("%%%%%%%%\n%ABBDD %\n%%%%%%%%")
        self.assertIsNone(step(layout.board, layout.single_state(), Action.EAST))

    def test_wall_and_wait_are_illegal_single(self):
        layout = load_map(ROOT / "maps/single/tiny.txt")
        for action in (Action.NORTH, Action.WAIT):
            self.assertIsNone(step(layout.board, layout.single_state(), action))

    def test_open_map_rejected(self):
        with self.assertRaisesRegex(ValueError, "enclosed"):
            parse_map("%%%%%\n%ABD \n%%%%%")

    def test_irregular_reference_is_enclosed(self):
        layout = load_map(ROOT / "maps/single/reference_transcribed.txt")
        self.assertEqual(len(layout.boxes), 7)
        self.assertEqual(len(layout.board.goals), 7)
        self.assertNotIn((0, 0), layout.board.floors)

    def test_replay_and_branch(self):
        layout = load_map(ROOT / "maps/single/tiny.txt")
        states = replay(layout.board, layout.single_state(), (Action.EAST,))
        history = History(states)
        history.forward()
        self.assertTrue(is_goal(layout.board, history.current))
        history.backward()
        self.assertEqual(history.current, layout.single_state())
        history.append(states[-1])
        self.assertEqual(len(history.states), 2)

    def test_invalid_solution_rejected(self):
        layout = load_map(ROOT / "maps/single/tiny.txt")
        with self.assertRaises(ValueError):
            validate_result(layout.board, layout.single_state(), SearchResult(Status.SOLVED, (), 0))

    def test_solved_initial_state(self):
        layout = load_map(ROOT / "maps/single/already_solved.txt")
        validate_result(layout.board, layout.single_state(), SearchResult(Status.SOLVED, (), 0))

    def test_unordered_boxes_have_identical_keys(self):
        self.assertEqual(State((1, 1), frozenset([(2, 2), (3, 3)])),
                         State((1, 1), frozenset([(3, 3), (2, 2)])))

    def test_two_box_map_manual_solution(self):
        layout = load_map(ROOT / "maps/single/two_boxes.txt")
        actions = [Action.EAST, Action.EAST, Action.EAST, Action.WEST, Action.WEST,
                   Action.SOUTH, Action.EAST, Action.EAST]
        final = replay(layout.board, layout.single_state(), actions)[-1]
        self.assertTrue(is_goal(layout.board, final))

    def test_competition_initialization_only(self):
        layout = load_map(ROOT / "maps/competitive/arena.txt", competitive=True)
        engine = CompetitionEngine(layout, 50)
        self.assertEqual(engine.scores(engine.initial), (0, 0))
        self.assertFalse(engine.finished(engine.initial))
        next_state = engine.step(engine.initial, (Action.WAIT, Action.WAIT))
        self.assertEqual(next_state.round_index, 1)
        self.assertEqual(next_state.players, engine.initial.players)


if __name__ == "__main__":
    unittest.main()
