"""Run the same controller contract checks for Phuong's implementation."""
from test_agent_one import AgentOneTests as _AgentOneTests
from sokoban.competitive.agent_two import AgentTwo


class AgentTwoTests(_AgentOneTests):
    def setUp(self):
        super().setUp()
        self.agent = AgentTwo()

    def test_node_limit_returns_wait(self):
        from sokoban.competitive.contracts import Observation
        from sokoban.core.model import Action
        from time import perf_counter
        action = AgentTwo(max_expanded=1).choose_action(
            Observation(self.layout.board, self.engine.initial, 0), perf_counter() + 2)
        self.assertEqual(action, Action.WAIT)


# Avoid unittest collecting the imported base test class a second time.
del _AgentOneTests
