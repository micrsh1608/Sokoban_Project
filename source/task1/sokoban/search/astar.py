"""A* graph search for Sokoban. Owner: Phuong."""
from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from ..core.model import Action, Board, State
from ..core.rules import is_goal, successors
from .contracts import SearchLimits, SearchMetrics, SearchResult, Status
from .heuristics import Heuristic


def solve(board: Board, initial: State, limits: SearchLimits) -> SearchResult:
    start = perf_counter()
    deadline = start + limits.seconds
    heuristic = Heuristic(board)
    preprocess_end = perf_counter()
    preprocess_ms = (preprocess_end - start) * 1000
    metrics = SearchMetrics(preprocess_ms=preprocess_ms,
                            max_frontier=1, max_reached=1)

    if preprocess_end >= deadline:
        return SearchResult(Status.TIMEOUT, metrics=metrics,
                            message="Search time limit reached during heuristic preprocessing.")

    order = count()
    initial_h = heuristic(initial)
    frontier = [(initial_h, next(order), 0, initial)]
    best_g = {initial: 0}
    parents: dict[State, tuple[State, Action]] = {}

    while frontier:
        if perf_counter() >= deadline:
            return SearchResult(Status.TIMEOUT, metrics=metrics,
                                message="Search time limit reached; solvability is unknown.")

        _, _, cost, state = heappop(frontier)
        if cost != best_g[state]:
            continue

        if is_goal(board, state):
            actions = []
            cursor = state
            while cursor != initial:
                cursor, action = parents[cursor]
                actions.append(action)
            actions.reverse()
            return SearchResult(Status.SOLVED, tuple(actions), cost, metrics,
                                "A* found a minimum-cost solution.")

        if metrics.expanded >= limits.max_expanded:
            return SearchResult(Status.LIMIT_REACHED, metrics=metrics,
                                message="Expansion limit reached; solvability is unknown.")

        metrics.expanded += 1
        for transition in successors(board, state):
            metrics.generated += 1
            if perf_counter() >= deadline:
                return SearchResult(Status.TIMEOUT, metrics=metrics,
                                    message="Search time limit reached; solvability is unknown.")
            child = transition.state
            new_cost = cost + transition.cost
            if new_cost < best_g.get(child, float("inf")):
                best_g[child] = new_cost
                parents[child] = (state, transition.action)
                priority = new_cost + heuristic(child)
                heappush(frontier, (priority, next(order), new_cost, child))
                metrics.max_frontier = max(metrics.max_frontier, len(frontier))
                metrics.max_reached = max(metrics.max_reached, len(best_g))

    return SearchResult(Status.UNSOLVABLE, metrics=metrics,
                        message="Frontier exhausted; no solution exists in the reachable state space.")
