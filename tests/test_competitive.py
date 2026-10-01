from dataclasses import replace
from itertools import product
from pathlib import Path
import random
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source/task1'))
from sokoban.core.model import Action, Board, Layout
from sokoban.competitive.contracts import Box
from sokoban.competitive.engine import CompetitionEngine
W, N, E, S, L = Action.WAIT, Action.NORTH, Action.EAST, Action.SOUTH, Action.WEST


def room(players=((2, 1), (4, 6)), boxes=((2, 2),), goals=None, rounds=10):
    floors = frozenset((r, c) for r in range(1, 6) for c in range(1, 8))
    walls = frozenset((r, c) for r in range(7) for c in range(9)) - floors
    if goals is None: goals = [(5, 7-i) for i in range(len(boxes))]
    board = Board(9, 7, walls, floors, frozenset(goals))
    return CompetitionEngine(Layout(board, tuple(players), frozenset(boxes)), rounds)


class CompetitionTests(unittest.TestCase):
    def test_independent_moves_and_immutable_input(self):
        e = room(); out = e.resolve(e.initial, (N, L))
        self.assertEqual(out.state.players, ((1, 1), (4, 5)))
        self.assertEqual(out.moved, (True, True))
        self.assertEqual(e.initial.players, ((2, 1), (4, 6)))
        self.assertEqual(e.initial.round_index, 0)

    def test_wait_advances_round(self):
        e = room(); out = e.resolve(e.initial, (W, W))
        self.assertEqual(out.state.round_index, 1)
        self.assertEqual(out.state.boxes, e.initial.boxes)
        self.assertEqual(out.reasons, ('wait', 'wait'))

    def test_wall_does_not_block_other(self):
        e = room(players=((1, 1), (4, 6)))
        self.assertEqual(e.resolve(e.initial, (N, L)).moved, (False, True))

    def test_same_cell_cancels_both(self):
        e = room(players=((3, 2), (3, 4))); out = e.resolve(e.initial, (E, L))
        self.assertEqual(out.state.players, e.initial.players)
        self.assertEqual(out.reasons, ('conflict_destination',)*2)

    def test_swap_forbidden(self):
        e = room(players=((3, 2), (3, 3)))
        self.assertEqual(e.resolve(e.initial, (E, L)).reasons, ('blocked_player',)*2)

    def test_follow_into_vacated_cell_forbidden(self):
        e = room(players=((3, 2), (3, 3)))
        self.assertEqual(e.step(e.initial, (E, E)).players, ((3, 2), (3, 4)))

    def test_push_to_goal_assigns_owner(self):
        e = room(goals=((2, 3),)); s = e.step(e.initial, (E, W))
        self.assertEqual(s.boxes[0], Box(0, (2, 3), 0))
        self.assertEqual(e.scores(s), (1, 0))

    def test_push_off_goal_clears_owner(self):
        e = room(boxes=((2, 3),), goals=((2, 3),), players=((2, 2), (4, 6)))
        s = e.step(replace(e.initial, boxes=(Box(0, (2, 3), 1),)), (E, W))
        self.assertIsNone(s.boxes[0].owner)
        self.assertEqual(e.scores(s), (0, 0))

    def test_initial_c_neutral_and_no_early_end(self):
        e = room(boxes=((2, 3),), goals=((2, 3),))
        self.assertEqual(e.scores(e.initial), (0, 0)); self.assertFalse(e.finished(e.initial))

    def test_stationary_box_keeps_owner(self):
        e = room(boxes=((2, 3),), goals=((2, 3),))
        state = replace(e.initial, boxes=(Box(0, (2, 3), 1),))
        self.assertEqual(e.step(state, (W, W)).boxes, state.boxes)

    def test_goal_to_goal_updates_owner(self):
        e = room(players=((2, 2), (4, 6)), boxes=((2, 3), (4, 4)), goals=((2, 3), (2, 4)))
        state = replace(e.initial, boxes=(Box(0, (2, 3), 1), Box(1, (4, 4))))
        s = e.step(state, (E, W))
        self.assertEqual(s.boxes[0], Box(0, (2, 4), 0)); self.assertEqual(e.scores(s), (1, 0))

    def test_box_wall_block(self):
        e = room(players=((2, 6), (4, 6)), boxes=((2, 7),))
        self.assertEqual(e.resolve(e.initial, (E, W)).reasons[0], 'blocked_box_wall_or_void')

    def test_box_box_block_even_when_other_moves(self):
        e = room(players=((3, 1), (2, 3)), boxes=((3, 2), (3, 3)))
        out = e.resolve(e.initial, (E, S))
        self.assertEqual(out.reasons[0], 'blocked_box_box'); self.assertEqual(out.moved, (False, True))

    def test_box_player_block_even_when_other_moves(self):
        e = room(players=((3, 1), (3, 3)), boxes=((3, 2),))
        out = e.resolve(e.initial, (E, S))
        self.assertEqual(out.reasons[0], 'blocked_box_player'); self.assertEqual(out.moved, (False, True))

    def test_same_box_perpendicular_pushes(self):
        e = room(players=((3, 2), (2, 3)), boxes=((3, 3),))
        out = e.resolve(e.initial, (E, S))
        self.assertEqual(out.reasons, ('conflict_same_box',)*2)
        self.assertEqual(out.state.boxes, e.initial.boxes)

    def test_same_box_opposite_pushes(self):
        e = room(players=((3, 2), (3, 4)), boxes=((3, 3),))
        self.assertEqual(e.resolve(e.initial, (E, L)).moved, (False, False))

    def test_two_boxes_same_destination(self):
        e = room(players=((3, 1), (3, 5)), boxes=((3, 2), (3, 4)))
        out = e.resolve(e.initial, (E, L))
        self.assertEqual(out.reasons, ('conflict_destination',)*2)
        self.assertEqual(out.state.boxes, e.initial.boxes)

    def test_box_player_same_destination(self):
        e = room(players=((3, 1), (2, 3)), boxes=((3, 2),))
        self.assertEqual(e.resolve(e.initial, (E, S)).reasons, ('conflict_destination',)*2)

    def test_two_independent_pushes_score_together(self):
        e = room(players=((2, 1), (4, 6)), boxes=((2, 2), (4, 5)), goals=((2, 3), (4, 4)))
        s = e.step(e.initial, (E, L))
        self.assertEqual(e.scores(s), (1, 1)); self.assertEqual(s.round_index, 1)

    def test_invalid_action_wait(self):
        e = room(); out = e.resolve(e.initial, (None, 'West'))
        self.assertEqual(out.actions, (W, L)); self.assertEqual(out.reasons, ('invalid_action', 'moved'))

    def test_malformed_pairs(self):
        e = room()
        for bad in [None, 'East', (W,), (W, W, W)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): e.step(e.initial, bad)

    def test_invalid_n(self):
        for n in [0, -1, True, 1.5, '10']:
            with self.subTest(n=n), self.assertRaises(ValueError): room(rounds=n)

    def test_draw_end_and_extra_round(self):
        e = room(rounds=1); s = e.step(e.initial, (W, W))
        self.assertTrue(e.finished(s)); self.assertIsNone(e.winner(s))
        with self.assertRaises(ValueError): e.step(s, (W, W))
        with self.assertRaises(ValueError): e.winner(e.initial)

    def test_winner_both_sides(self):
        e = room(goals=((2, 3),), rounds=1)
        self.assertEqual(e.winner(e.step(e.initial, (E, W))), 0)
        e = room(players=((4, 6), (2, 1)), goals=((2, 3),), rounds=1)
        self.assertEqual(e.winner(e.step(e.initial, (W, E))), 1)

    def test_corrupt_snapshots_rejected(self):
        e = room()
        bad = [replace(e.initial, players=((2, 1), (2, 1))),
               replace(e.initial, players=((2, 2), (4, 6))),
               replace(e.initial, boxes=(Box(99, (2, 2)),)),
               replace(e.initial, boxes=(Box(0, (2, 2), 0),)),
               replace(e.initial, round_index=11)]
        for s in bad:
            with self.subTest(state=s), self.assertRaises(ValueError): e.step(s, (W, W))

    def test_full_steal_sequence(self):
        e = room(players=((3, 1), (4, 2)), boxes=((3, 2),), goals=((3, 3),), rounds=8)
        state = e.initial; scores = []
        for joint in [(E, W), (N, E), (L, N), (W, L), (W, N), (W, N), (W, E), (W, S)]:
            state = e.step(state, joint); scores.append(e.scores(state))
        self.assertEqual(scores, [(1,0), (1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,1)])
        self.assertEqual(e.winner(state), 1)

    def test_1000_joint_cases_invariants_and_swap_symmetry(self):
        rng = random.Random(20261001)
        positions = [(r,c) for r in range(1,6) for c in range(1,8)]
        for _ in range(40):
            a,b,x,y = rng.sample(positions,4)
            e = room(players=(a,b), boxes=(x,y)); swapped = replace(e.initial, players=(b,a))
            for actions in product(list(Action), repeat=2):
                out = e.resolve(e.initial, actions); other = e.resolve(swapped, actions[::-1])
                self.assertEqual(out.state.players, other.state.players[::-1])
                self.assertEqual(out.moved, other.moved[::-1]); self.assertEqual(out.reasons, other.reasons[::-1])
                mirrored = tuple(replace(box, owner=None if box.owner is None else 1-box.owner) for box in other.state.boxes)
                self.assertEqual(out.state.boxes, mirrored)
                self.assertEqual(out.state.round_index,1); self.assertEqual(e.initial.round_index,0)
                e.validate_state(out.state)

if __name__ == '__main__': unittest.main()
