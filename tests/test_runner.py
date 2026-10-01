from pathlib import Path
import sys
import json
import multiprocessing as mp
import tempfile
from time import perf_counter
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source/task1'))
sys.path.insert(0,str(ROOT/'tests'))
from sokoban.core.parser import load_map
from sokoban.core.model import Action
from sokoban.competitive.engine import CompetitionEngine
from sokoban.competitive.runner import run_match, AGENT_ONE, WAIT_AGENT


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.layout=load_map(ROOT/'maps/competitive/arena.txt',competitive=True)
        self.before_children={p.pid for p in mp.active_children()}

    def tearDown(self):
        self.assertEqual({p.pid for p in mp.active_children()},self.before_children)

    def test_agent_one_scores_and_log_replays(self):
        engine=CompetitionEngine(self.layout,5)
        callbacks=[]
        result=run_match(engine,on_turn=callbacks.append)
        self.assertEqual(result.scores,(1,0))
        self.assertEqual(len(result.turns),5)
        self.assertEqual(len(callbacks),5)
        state=engine.initial
        for record in result.turns:
            self.assertEqual(record.before,state)
            state=engine.step(state,tuple(d.action for d in record.decisions))
            self.assertEqual(state,record.after)
            self.assertTrue(all(d.elapsed_ms<1000 for d in record.decisions if d.status=='ok'))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'match.json'; result.save(path)
            data=json.loads(path.read_text())
            self.assertEqual(data['scores'],[1,0])
            self.assertEqual(len(data['turns']),5)
            self.assertIn('goals',data['board'])

    def test_both_observe_same_pre_round_snapshot(self):
        spec='runner_fixtures:SnapshotAgent'
        result=run_match(CompetitionEngine(self.layout,1),(spec,spec))
        self.assertEqual([d.status for d in result.turns[0].decisions],['ok','ok'])
        self.assertEqual(result.turns[0].after.players,((1,2),(3,10)))

    def test_hang_becomes_wait_and_worker_restarts(self):
        start=perf_counter()
        result=run_match(CompetitionEngine(self.layout,2),('runner_fixtures:HangAgent',WAIT_AGENT),decision_ms=150)
        self.assertLess(perf_counter()-start,8)
        self.assertEqual([r.decisions[0].status for r in result.turns],['timeout','timeout'])
        self.assertTrue(all(r.decisions[0].action==Action.WAIT for r in result.turns))
        self.assertTrue(all(r.decisions[1].status=='ok' for r in result.turns))

    def test_exception_and_invalid_return(self):
        result=run_match(CompetitionEngine(self.layout,2),
                         ('runner_fixtures:ErrorAgent','runner_fixtures:InvalidAgent'))
        for r in result.turns:
            self.assertEqual([d.status for d in r.decisions],['error','invalid_action'])
            self.assertEqual([d.action for d in r.decisions],[Action.WAIT,Action.WAIT])

    def test_startup_failure_cleans_workers(self):
        with self.assertRaises(RuntimeError):
            run_match(CompetitionEngine(self.layout,1),(WAIT_AGENT,'runner_fixtures:BrokenConstructor'))

    def test_callback_exception_cleans_workers(self):
        def fail(record): raise RuntimeError('UI callback test')
        with self.assertRaises(RuntimeError):
            run_match(CompetitionEngine(self.layout,1),(WAIT_AGENT,WAIT_AGENT),on_turn=fail)

    def test_budget_validation(self):
        for budget in (0,1001,True,1.5):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                run_match(CompetitionEngine(self.layout,1),decision_ms=budget)

if __name__=='__main__': unittest.main()
