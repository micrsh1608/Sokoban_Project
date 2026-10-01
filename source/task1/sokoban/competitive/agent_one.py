"""Bounded BFS controller. Replans each round, predicts the opponent will Wait.

This is a legal local policy, not minimax and not a guaranteed winning strategy.
"""
from collections import deque
from time import perf_counter
from ..core.model import Action, DIRECTIONS, Layout
from .contracts import Observation
from .engine import CompetitionEngine


class AgentOne:
    def __init__(self, max_expanded: int = 5000):
        if type(max_expanded) is not int or max_expanded <= 0:
            raise ValueError('max_expanded must be a positive integer')
        self.max_expanded = max_expanded
        self.last_stats = {}

    def choose_action(self, observation: Observation, deadline: float) -> Action:
        self.last_stats = {'expanded': 0, 'reason': 'no_improvement'}
        if perf_counter() >= deadline:
            self.last_stats['reason'] = 'deadline'
            return Action.WAIT
        me = observation.agent_id
        if me not in (0, 1):
            raise ValueError('agent_id must be 0 or 1')
        board, initial = observation.board, observation.state
        layout = Layout(board, initial.players, frozenset(b.position for b in initial.boxes))
        engine = CompetitionEngine(layout, initial.max_rounds)
        engine.validate_state(initial)
        if engine.finished(initial):
            self.last_stats['reason'] = 'finished'
            return Action.WAIT
        base_scores = engine.scores(initial)
        base_value = base_scores[me] - base_scores[1-me]
        # Time (round) is excluded: identical physical states reached later do
        # not improve a shortest path when the simulated opponent always waits.
        def key(state):
            return state.players, state.boxes
        queue = deque([(initial, None)])
        seen = {key(initial)}
        while queue:
            if perf_counter() >= deadline:
                self.last_stats['reason'] = 'deadline'
                return Action.WAIT
            state, first_action = queue.popleft()
            if state.round_index >= initial.max_rounds:
                continue
            if self.last_stats['expanded'] >= self.max_expanded:
                self.last_stats['reason'] = 'node_limit'
                return Action.WAIT
            self.last_stats['expanded'] += 1
            for action in DIRECTIONS:
                if perf_counter() >= deadline:
                    self.last_stats['reason'] = 'deadline'
                    return Action.WAIT
                joint = [Action.WAIT, Action.WAIT]
                joint[me] = action
                outcome = engine.resolve(state, tuple(joint))
                if not outcome.moved[me]:
                    continue
                child = outcome.state
                child_key = key(child)
                if child_key in seen:
                    continue
                seen.add(child_key)
                first = action if first_action is None else first_action
                scores = engine.scores(child)
                if scores[me] - scores[1-me] > base_value:
                    self.last_stats['reason'] = 'score_improvement'
                    self.last_stats['plan_steps'] = child.round_index - initial.round_index
                    return first
                queue.append((child, first))
        return Action.WAIT
