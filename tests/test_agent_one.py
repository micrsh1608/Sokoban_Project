from pathlib import Path
import sys
from dataclasses import replace
from time import perf_counter
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source/task1'))
from sokoban.core.parser import load_map
from sokoban.core.model import Action
from sokoban.competitive.contracts import Observation
from sokoban.competitive.engine import CompetitionEngine
from sokoban.competitive.agent_one import AgentOne


class AgentOneTests(unittest.TestCase):
    def setUp(self):
        self.layout=load_map(ROOT/'maps/competitive/arena.txt',competitive=True)
        self.engine=CompetitionEngine(self.layout,20)
        self.agent=AgentOne()

    def test_finds_nearby_score_plan(self):
        obs=Observation(self.layout.board,self.engine.initial,0)
        action=self.agent.choose_action(obs,perf_counter()+2)
        self.assertEqual(action,Action.EAST)
        self.assertEqual(self.agent.last_stats['plan_steps'],3)

    def test_replanning_reaches_goal(self):
        s=self.engine.initial
        for _ in range(3):
            action=self.agent.choose_action(Observation(self.layout.board,s,0),perf_counter()+2)
            s=self.engine.step(s,(action,Action.WAIT))
        self.assertEqual(self.engine.scores(s),(1,0))

    def test_supports_other_agent_id(self):
        s=replace(self.engine.initial,players=self.engine.initial.players[::-1])
        action=self.agent.choose_action(Observation(self.layout.board,s,1),perf_counter()+2)
        self.assertEqual(action,Action.EAST)

    def test_expired_deadline_returns_wait(self):
        action=self.agent.choose_action(Observation(self.layout.board,self.engine.initial,0),perf_counter()-1)
        self.assertEqual(action,Action.WAIT)
        self.assertEqual(self.agent.last_stats['reason'],'deadline')

    def test_node_limit_returns_wait(self):
        action=AgentOne(max_expanded=1).choose_action(
            Observation(self.layout.board,self.engine.initial,0),perf_counter()+2)
        self.assertEqual(action,Action.WAIT)

    def test_cannot_plan_beyond_remaining_rounds(self):
        s=replace(self.engine.initial,round_index=19)
        action=self.agent.choose_action(Observation(self.layout.board,s,0),perf_counter()+2)
        self.assertEqual(action,Action.WAIT)

    def test_finished_match_wait(self):
        s=replace(self.engine.initial,round_index=20)
        self.assertEqual(self.agent.choose_action(Observation(self.layout.board,s,0),perf_counter()+2),Action.WAIT)

if __name__=='__main__': unittest.main()
