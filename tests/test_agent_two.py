from pathlib import Path
import sys
import unittest
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/task1"))

from sokoban.core.model import Action
from sokoban.core.parser import load_map
from sokoban.competitive.agent_two import AgentTwo
from sokoban.competitive.contracts import Observation
from sokoban.competitive.engine import CompetitionEngine


class AgentTwoTests(unittest.TestCase):
    def setUp(self):
        self.layout = load_map(ROOT / "maps/competitive/arena.txt", competitive=True)
        self.engine = CompetitionEngine(self.layout, 20)
        self.agent = AgentTwo()

    def test_finds_first_east_push(self):
        action = self.agent.choose_action(
            Observation(self.layout.board, self.engine.initial, 0),
            perf_counter() + 2,
        )
        self.assertEqual(action, Action.EAST)
        self.assertEqual(self.agent.last_stats["reason"], "score_improvement")

    def test_supports_agent_one_side(self):
        action = self.agent.choose_action(
            Observation(self.layout.board, self.engine.initial, 1),
            perf_counter() + 2,
        )
        self.assertEqual(action, Action.WEST)

    def test_expired_deadline_returns_wait(self):
        action = self.agent.choose_action(
            Observation(self.layout.board, self.engine.initial, 0),
            perf_counter() - 1,
        )
        self.assertEqual(action, Action.WAIT)
        self.assertEqual(self.agent.last_stats["reason"], "deadline")

    def test_node_limit_returns_wait(self):
        limited_agent = AgentTwo(max_expanded=1)
        action = limited_agent.choose_action(
            Observation(self.layout.board, self.engine.initial, 0),
            perf_counter() + 2,
        )
        self.assertEqual(action, Action.WAIT)
        self.assertEqual(limited_agent.last_stats.get("reason"), "node_limit")

    def test_finished_match_waits(self):
        state = self.engine.initial
        for _ in range(20):
            state = self.engine.step(state, (Action.WAIT, Action.WAIT))
        action = self.agent.choose_action(
            Observation(self.layout.board, state, 0),
            perf_counter() + 2,
        )
        self.assertEqual(action, Action.WAIT)


if __name__ == "__main__":
    unittest.main()
