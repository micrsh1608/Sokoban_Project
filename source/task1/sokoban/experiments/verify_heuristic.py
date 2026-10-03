"""Phuong: checker is ready; exact-cost dataset generation is still required."""
from math import isfinite
from ..core.rules import is_goal, successors


def check_samples(board, heuristic, exact_costs: dict) -> dict:
    """exact_costs maps solvable State -> true optimal remaining cost (not A* estimates).

    Enumerate small state spaces and use UCS or reverse shortest paths as oracle.
    A timeout is unknown, NEVER an infinite exact cost. Report sample coverage.
    This checker alone is not a proof for every Sokoban map.
    """
    if not exact_costs:
        raise ValueError("Cannot verify using an empty dataset.")
    violations = []
    edges = 0
    for state, optimal in exact_costs.items():
        if not isfinite(optimal) or optimal < 0:
            raise ValueError("Only finite, nonnegative, exact costs are accepted.")
        value = heuristic(state)
        if not isfinite(value) or value < 0 or value > optimal:
            violations.append(("admissibility", repr(state), value, optimal))
        if is_goal(board, state) and value != 0:
            violations.append(("goal_not_zero", repr(state), value))
        for transition in successors(board, state):
            edges += 1
            next_value = heuristic(transition.state)
            if next_value != next_value or next_value < 0 or value > transition.cost + next_value:
                violations.append(("consistency", repr(state), transition.action.value))
    return {"states_checked": len(exact_costs), "edges_checked": edges,
            "violations": violations, "scope": "sampled states only; not a global proof"}
