"""AgentTwo: deadline-aware A* replanning controller.

The controller uses A* to find a short sequence that improves the current
score difference while predicting the other agent as Wait during simulation.
The real engine still resolves both agents simultaneously.
"""
from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from ..core.model import Action, DIRECTIONS, Layout
from ..search.heuristics import Heuristic
from .contracts import Observation
from .engine import CompetitionEngine


class AgentTwo:
    def __init__(self, max_expanded: int = 5000):
        if type(max_expanded) is not int or max_expanded <= 0:
            raise ValueError("max_expanded must be a positive integer")
        self.max_expanded = max_expanded
        self.last_stats = {}

    @staticmethod
    def _key(state):
        boxes = tuple(sorted((box.id, box.position, box.owner)
                             for box in state.boxes))
        return state.players, boxes

    def choose_action(self, observation: Observation, deadline: float) -> Action:
        self.last_stats = {"expanded": 0, "reason": "no_improvement"}
        if perf_counter() >= deadline:
            self.last_stats["reason"] = "deadline"
            return Action.WAIT

        me = observation.agent_id
        if me not in (0, 1):
            raise ValueError("agent_id must be 0 or 1")

        board = observation.board
        initial = observation.state
        layout = Layout(board, initial.players,
                        frozenset(box.position for box in initial.boxes))
        engine = CompetitionEngine(layout, initial.max_rounds)
        engine.validate_state(initial)
        if engine.finished(initial):
            self.last_stats["reason"] = "finished"
            return Action.WAIT

        base_scores = engine.scores(initial)
        base_value = base_scores[me] - base_scores[1 - me]
        heuristic = Heuristic(board)
        order = count()

        # A* state cost is the number of simulated rounds.  The heuristic is
        # a lower bound on pushes still needed to move boxes toward goals.
        initial_h = heuristic.minimum_push_distance(
            box.position for box in initial.boxes
        )
        frontier = [(initial_h, next(order), 0, initial, None)]
        best_g = {self._key(initial): 0}

        while frontier:
            if perf_counter() >= deadline:
                self.last_stats["reason"] = "deadline"
                return Action.WAIT
            _, _, cost, state, first_action = heappop(frontier)
            key = self._key(state)
            if cost != best_g.get(key):
                continue

            if cost > 0:
                scores = engine.scores(state)
                if scores[me] - scores[1 - me] > base_value:
                    self.last_stats["reason"] = "score_improvement"
                    self.last_stats["plan_steps"] = cost
                    return first_action

            if state.round_index >= initial.max_rounds:
                continue
            if self.last_stats["expanded"] >= self.max_expanded:
                self.last_stats["reason"] = "node_limit"
                return Action.WAIT

            self.last_stats["expanded"] += 1
            for action in DIRECTIONS:
                if perf_counter() >= deadline:
                    self.last_stats["reason"] = "deadline"
                    return Action.WAIT
                outcome = engine.resolve(state, (action, Action.WAIT)
                                         if me == 0 else (Action.WAIT, action))
                if not outcome.moved[me]:
                    continue
                child = outcome.state
                child_key = self._key(child)
                new_cost = cost + 1
                if new_cost >= best_g.get(child_key, float("inf")):
                    continue
                best_g[child_key] = new_cost
                first = action if first_action is None else first_action
                h = heuristic.minimum_push_distance(
                    box.position for box in child.boxes
                )
                heappush(frontier, (new_cost + h, next(order), new_cost,
                                    child, first))

        return Action.WAIT

