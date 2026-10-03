"""GUI regression checks with SDL dummy driver; no real display required."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from pathlib import Path
import sys
from concurrent.futures import Future
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source/task1'))
from sokoban.core.parser import load_map
from sokoban.search.contracts import SearchLimits
from sokoban.ui.app import App
from sokoban.ui.competitive import CompetitiveApp


class UIIntegrationTests(unittest.TestCase):
    def test_gui_smoke_exits_without_quit_event(self):
        app = App(load_map(ROOT / 'maps/single/tiny.txt'), SearchLimits())
        # On the old code this raises on frame 2 instead of hanging CI forever.
        with patch('pygame.event.get', side_effect=[[], AssertionError('smoke did not exit')]):
            app.run(smoke=True)

    def test_no_duplicate_solve_requests(self):
        app = App(load_map(ROOT / 'maps/single/tiny.txt'), SearchLimits())
        try:
            pending = Future()
            with patch.object(app.executor, 'submit', return_value=pending) as submit:
                app.solve()
                app.solve()
                self.assertEqual(submit.call_count, 1)
                self.assertIs(app.future, pending)
        finally:
            app.close()

    def test_async_result_replays_and_steps_back(self):
        for algorithm in ('ucs', 'astar'):
            app = App(load_map(ROOT / 'maps/single/two_boxes.txt'), SearchLimits(), algorithm)
            try:
                app.solve()
                app.future.result(timeout=5)
                app.check_future()
                self.assertEqual(len(app.solution_actions), 8)
                self.assertEqual(app.solution_cost, 8)
                for _ in range(8):
                    app.forward()
                self.assertTrue(app.is_goal(app.current_state))
                app.backward()
                self.assertEqual(app.current_index, 7)
                self.assertEqual(app.solution_cost, 8)
                self.assertEqual(len(app.solution_actions), 8)
            finally:
                app.close()

    def test_competitive_done_preserves_paused_frame(self):
        app = CompetitiveApp(load_map(ROOT / 'maps/competitive/arena.txt', True))
        state = app.engine.step(app.engine.initial, ('Wait', 'Wait'))
        app.queue.put(('turn', SimpleNamespace(after=state, scores=(0, 0), reasons=('', ''))))
        app.queue.put(('done', SimpleNamespace(winner=None)))
        app.process_queue()
        self.assertEqual(app.current_index, 0)
        self.assertEqual(len(app.snapshots), 2)
        app.forward()
        self.assertEqual(app.current_state, state)

    def test_competitive_smoke(self):
        app = CompetitiveApp(load_map(ROOT / 'maps/competitive/arena.txt', True))
        app.run(smoke=True)

    def test_competitive_thread_runs_real_match_and_closes(self):
        import multiprocessing as mp
        before = {p.pid for p in mp.active_children()}
        app = CompetitiveApp(load_map(ROOT / 'maps/competitive/arena.txt', True), rounds=8)
        try:
            app.start_match()
            app.worker.join(timeout=15)
            self.assertFalse(app.worker.is_alive())
            app.process_queue()
            self.assertEqual(len(app.snapshots), 9)
            self.assertTrue(app.finished)
        finally:
            app.close()
        self.assertEqual({p.pid for p in mp.active_children()}, before)


class MergedGUIRegressionTests(unittest.TestCase):
    def make_app(self, **kwargs):
        return CompetitiveApp(load_map(ROOT / 'maps/competitive/arena.txt', True), **kwargs)

    def test_live_queue_does_not_skip_replay_frames(self):
        app = self.make_app()
        app.paused = False
        state = app.engine.step(app.engine.initial, ('Wait', 'Wait'))
        app.queue.put(('turn', SimpleNamespace(after=state, scores=(0, 0), reasons=('', ''))))
        app.process_queue()
        self.assertEqual(app.current_index, 0)
        self.assertEqual(len(app.snapshots), 2)

    def test_invalid_round_input_does_not_start_worker(self):
        app = self.make_app()
        app.round_text = '0'
        app.start_match()
        self.assertFalse(app.running_match)
        self.assertIsNone(app.worker)

    def test_round_input_and_gui_match_log(self):
        import tempfile
        import json
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'match.json'
            app = self.make_app(match_output=output)
            app.round_text = '3'
            try:
                app.start_match()
                app.worker.join(timeout=15)
                self.assertFalse(app.worker.is_alive())
                app.process_queue()
                data = json.loads(output.read_text())
                self.assertEqual(len(data['turns']), 3)
                self.assertIn('agent_two:AgentTwo', data['controllers'][1])
                self.assertEqual(len(app.snapshots), 4)
                self.assertEqual(app.current_index, 0)
            finally:
                app.close()
