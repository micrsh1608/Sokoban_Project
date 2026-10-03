"""Persistent spawn workers; concurrent decisions from the same pre-round state.

Deadline overruns/errors become Wait. Process cleanup is outside decision time.
This is process isolation for reliability, not a sandbox for malicious code.
"""
from dataclasses import asdict, dataclass
import importlib
import json
import multiprocessing as mp
from multiprocessing.connection import wait
from pathlib import Path
from threading import Event
from time import perf_counter
from ..core.model import Action
from .contracts import Observation

AGENT_ONE = 'sokoban.competitive.agent_one:AgentOne'
AGENT_TWO = 'sokoban.competitive.agent_two:AgentTwo'
WAIT_AGENT = 'sokoban.competitive.baseline_agent:WaitAgent'


class MatchCancelled(RuntimeError):
    """Raised when the caller requests a clean stop between agent decisions."""


@dataclass(frozen=True)
class Decision:
    action: Action
    status: str
    elapsed_ms: float
    compute_ms: float | None = None
    detail: str = ''


@dataclass(frozen=True)
class TurnRecord:
    round_index: int
    before: object
    after: object
    decisions: tuple[Decision, Decision]
    reasons: tuple[str, str]
    scores: tuple[int, int]


@dataclass(frozen=True)
class MatchResult:
    controllers: tuple[str, str]
    initial: object
    turns: tuple[TurnRecord, ...]
    scores: tuple[int, int]
    winner: int | None
    board: object
    decision_ms: int

    def save(self, path):
        # Board frozensets need an explicit stable JSON representation.
        data = asdict(self)
        data['board'] = {'width': self.board.width, 'height': self.board.height,
                         'walls': sorted(self.board.walls), 'floors': sorted(self.board.floors),
                         'goals': sorted(self.board.goals)}
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _worker(connection, spec):
    try:
        module_name, class_name = spec.split(':', 1)
        controller = getattr(importlib.import_module(module_name), class_name)()
        connection.send(('ready',))
        while True:
            request = connection.recv()
            if request is None:
                break
            round_id, observation, budget_seconds = request
            start = perf_counter()
            try:
                action = controller.choose_action(observation, start + budget_seconds)
                # Normalize inside worker: never send arbitrary controller objects.
                try:
                    action = Action(action)
                    status, detail = 'ok', ''
                except (ValueError, TypeError):
                    action, status, detail = Action.WAIT, 'invalid_action', 'Invalid return value'
            except Exception as exc:
                action, status = Action.WAIT, 'error'
                detail = f'{type(exc).__name__}: {exc}'[:300]
            elapsed = (perf_counter() - start) * 1000
            connection.send(('decision', round_id, action.value, status, elapsed, detail))
    except (EOFError, BrokenPipeError, OSError):
        pass
    except Exception as exc:
        try:
            connection.send(('startup_error', f'{type(exc).__name__}: {exc}'[:300]))
        except (OSError, EOFError):
            pass
    finally:
        connection.close()


class _Slot:
    def __init__(self, spec):
        self.spec = spec
        self.connection = None
        self.process = None

    def close(self):
        if self.process is not None:
            if self.process.pid is None:
                self.process.close()
                self.process = None
                if self.connection is not None:
                    self.connection.close()
                    self.connection = None
                return
            if self.process.is_alive():
                self.process.terminate()
            self.process.join(timeout=0.1)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=0.1)
            if not self.process.is_alive():
                self.process.close()
            self.process = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def start(self, cancel_event: Event | None = None):
        self.close()
        ctx = mp.get_context('spawn')
        parent, child = ctx.Pipe()
        self.connection = parent
        self.process = ctx.Process(target=_worker, args=(child, self.spec), daemon=True)
        try:
            self.process.start()
        except Exception:
            child.close()
            self.close()
            raise
        child.close()
        # Setup occurs before the round's 1000 ms decision clocks start.
        startup_deadline = perf_counter() + 5.0
        while not parent.poll(min(0.05, max(0.0, startup_deadline - perf_counter()))):
            if cancel_event is not None and cancel_event.is_set():
                self.close()
                raise MatchCancelled('Match cancelled during worker startup.')
            if perf_counter() >= startup_deadline:
                self.close()
                raise RuntimeError(f'Worker initialization timed out: {self.spec}')
        try:
            message = parent.recv()
        except EOFError as exc:
            self.close()
            raise RuntimeError(f'Worker failed to start: {self.spec}') from exc
        if message[0] != 'ready':
            self.close()
            raise RuntimeError(f'Worker startup failed: {message}')


def run_match(engine, agent_specs=(AGENT_ONE, WAIT_AGENT), decision_ms=1000, on_turn=None,
              cancel_event: Event | None = None):
    """Blocking match API. GUI should run it off its event loop.

    on_turn(record) runs in the caller thread, only after the joint commit.
    Timeout workers are destroyed; next round restarts them with fresh state.
    """
    if type(decision_ms) is not int or not 0 < decision_ms <= 1000:
        raise ValueError('decision_ms must be an integer from 1 to 1000')
    if len(agent_specs) != 2:
        raise ValueError('Exactly two controller specs are required')
    slots = [_Slot(spec) for spec in agent_specs]
    state, records = engine.initial, []
    try:
        for slot in slots:
            if cancel_event is not None and cancel_event.is_set():
                raise MatchCancelled('Match cancelled before startup.')
            slot.start(cancel_event)
        while not engine.finished(state):
            if cancel_event is not None and cancel_event.is_set():
                raise MatchCancelled('Match cancelled.')
            for slot in slots:
                if slot.process is None:
                    slot.start(cancel_event)
            before = state
            round_id = before.round_index + 1
            decisions = [None, None]
            starts, deadlines = {}, {}
            pending = {}
            # BOTH requests carry the exact same immutable before snapshot.
            for i, slot in enumerate(slots):
                starts[i] = perf_counter()
                deadlines[i] = starts[i] + decision_ms / 1000
                try:
                    slot.connection.send((round_id, Observation(engine.board, before, i),
                                          decision_ms / 1000 * 0.85))
                    pending[slot.connection] = i
                except (OSError, EOFError) as exc:
                    decisions[i] = Decision(Action.WAIT, 'error', (perf_counter()-starts[i])*1000,
                                            detail=str(exc)[:300])
            # A single wait set avoids giving the second controller extra time.
            while pending:
                if cancel_event is not None and cancel_event.is_set():
                    raise MatchCancelled('Match cancelled while waiting for decisions.')
                now = perf_counter()
                for conn, i in list(pending.items()):
                    if now >= deadlines[i]:
                        decisions[i] = Decision(Action.WAIT, 'timeout', (now-starts[i])*1000,
                                                detail='Response was not accepted before deadline')
                        del pending[conn]
                if not pending:
                    break
                timeout = min(0.05, max(0, min(deadlines[i] for i in pending.values()) - perf_counter()))
                for conn in wait(list(pending), timeout=timeout):
                    i = pending.pop(conn)
                    try:
                        message = conn.recv()
                        received = perf_counter()
                        if received >= deadlines[i]:
                            decisions[i] = Decision(Action.WAIT, 'timeout', (received-starts[i])*1000)
                        elif len(message) != 6 or message[0] != 'decision' or message[1] != round_id:
                            decisions[i] = Decision(Action.WAIT, 'error', (received-starts[i])*1000,
                                                    detail='Invalid or stale worker response')
                        else:
                            _, _, action, status, compute_ms, detail = message
                            decisions[i] = Decision(Action(action), status, (received-starts[i])*1000,
                                                    compute_ms, detail)
                    except (OSError, EOFError, ValueError, TypeError) as exc:
                        decisions[i] = Decision(Action.WAIT, 'error', (perf_counter()-starts[i])*1000,
                                                detail=str(exc)[:300])
            # Cleanup only after both decisions are resolved; no cleanup delay
            # can consume the other player's decision allowance.
            for i, decision in enumerate(decisions):
                if decision.status in ('timeout', 'error'):
                    slots[i].close()
            if cancel_event is not None and cancel_event.is_set():
                raise MatchCancelled('Match cancelled before committing the round.')
            result = engine.resolve(before, tuple(d.action for d in decisions))
            state = result.state
            record = TurnRecord(round_id, before, state, tuple(decisions), result.reasons, engine.scores(state))
            records.append(record)
            if on_turn is not None:
                on_turn(record)
        return MatchResult(tuple(agent_specs), engine.initial, tuple(records),
                           engine.scores(state), engine.winner(state), engine.board, decision_ms)
    finally:
        for slot in slots:
            slot.close()
