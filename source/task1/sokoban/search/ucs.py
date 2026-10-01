"""Uniform-cost graph search. Owner: Huy.

All game rules live in core.rules. The frontier is ordered by accumulated
cost g; the counter makes equal-cost entries comparable without ordering State.
"""
from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from ..core.model import Action, Board, State
from ..core.rules import is_goal, successors
from .contracts import SearchLimits, SearchMetrics, SearchResult, Status


def solve(board: Board, initial: State, limits: SearchLimits) -> SearchResult:
    deadline = perf_counter() + limits.seconds
    metrics = SearchMetrics(max_frontier=1, max_reached=1)
    order = count()
    frontier = [(0, next(order), initial)]
    best_g = {initial: 0}
    parents: dict[State, tuple[State, Action]] = {}

    while frontier:
        if perf_counter() >= deadline:
            return SearchResult(Status.TIMEOUT, metrics=metrics,
                                message="Search time limit reached; solvability is unknown.")

        cost, _, state = heappop(frontier)
        if cost != best_g[state]:
            # An improved entry was added later; ignore the old heap entry.
            continue

        # Test the goal on POP, never on generation. A generated goal may
        # still have a more expensive path than another route in the frontier.
        if is_goal(board, state):
            actions = []
            cursor = state
            while cursor != initial:
                cursor, action = parents[cursor]
                actions.append(action)
            actions.reverse()
            return SearchResult(Status.SOLVED, tuple(actions), cost, metrics,
                                "UCS found a minimum-cost solution.")

        # A goal already on the frontier can be accepted even if the last
        # permitted expansion just used up the expansion budget.
        if metrics.expanded >= limits.max_expanded:
            return SearchResult(Status.LIMIT_REACHED, metrics=metrics,
                                message="Expansion limit reached; solvability is unknown.")

        metrics.expanded += 1
        for transition in successors(board, state):
            metrics.generated += 1
            if perf_counter() >= deadline:
                return SearchResult(Status.TIMEOUT, metrics=metrics,
                                    message="Search time limit reached; solvability is unknown.")
            new_cost = cost + transition.cost
            child = transition.state
            if new_cost < best_g.get(child, float("inf")):
                best_g[child] = new_cost
                parents[child] = (state, transition.action)
                heappush(frontier, (new_cost, next(order), child))
                metrics.max_frontier = max(metrics.max_frontier, len(frontier))
                metrics.max_reached = max(metrics.max_reached, len(best_g))

    return SearchResult(Status.UNSOLVABLE, metrics=metrics,
                        message="Frontier exhausted: no solution exists under the game rules.")
