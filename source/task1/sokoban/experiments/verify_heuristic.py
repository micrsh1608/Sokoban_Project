"""Experimental checks for the Sokoban A* heuristic.

The exact remaining cost is obtained independently with UCS.  This is an
experiment over sampled states, not a proof over every possible Sokoban map.
"""
from collections import deque
from math import isfinite

from ..core.model import State
from ..core.rules import is_goal, successors
from ..search.contracts import SearchLimits, Status
from ..search.ucs import solve as ucs_solve


def reachable_states(board, initial, max_states=100):
    """Return a deterministic BFS sample of states reachable from initial."""
    if max_states <= 0:
        raise ValueError("max_states must be positive")
    queue = deque([initial])
    seen = {initial}
    result = []
    while queue and len(result) < max_states:
        state = queue.popleft()
        result.append(state)
        for transition in successors(board, state):
            if transition.state not in seen:
                seen.add(transition.state)
                queue.append(transition.state)
    return result, len(seen), bool(queue)


def generate_exact_costs(board, states, limits=None):
    """Use UCS as an independent optimal-cost oracle for sampled states.

    Only states for which UCS proves SOLVED or UNSOLVABLE are returned.  An
    unsolvable state is omitted because admissibility cannot be checked using
    an infinite/unknown value in the finite experiment.
    """
    limits = limits or SearchLimits(seconds=5.0, max_expanded=100_000)
    exact = {}
    skipped = []
    for state in states:
        result = ucs_solve(board, state, limits)
        if result.status == Status.SOLVED:
            exact[state] = result.total_cost
        else:
            skipped.append((state, result.status.value))
    return exact, skipped


def check_samples(board, heuristic, exact_costs: dict) -> dict:
    """Check admissibility and consistency on the supplied finite sample."""
    if not exact_costs:
        raise ValueError("Cannot verify using an empty dataset.")
    admissibility_violations = []
    consistency_violations = []
    edges = 0
    for state, optimal in exact_costs.items():
        if not isfinite(optimal) or optimal < 0:
            raise ValueError("Only finite, nonnegative, exact costs are accepted.")
        value = heuristic(state)
        if not isfinite(value) or value < 0 or value > optimal:
            admissibility_violations.append((repr(state), value, optimal))
        if is_goal(board, state) and value != 0:
            admissibility_violations.append(("goal_not_zero", repr(state), value))
        for transition in successors(board, state):
            edges += 1
            next_value = heuristic(transition.state)
            if (not isfinite(next_value) or next_value < 0
                    or value > transition.cost + next_value):
                consistency_violations.append(
                    (repr(state), transition.action.value, next_value)
                )
    return {
        "states_checked": len(exact_costs),
        "edges_checked": edges,
        "admissibility_violations": admissibility_violations,
        "consistency_violations": consistency_violations,
        "violations": admissibility_violations + consistency_violations,
        "scope": "sampled states only; not a global proof",
    }


def verify_map(board, initial, heuristic, max_states=72, oracle_limits=None):
    """Generate a finite exact-cost dataset and run both checks."""
    states, discovered, truncated = reachable_states(board, initial, max_states)
    exact_costs, skipped = generate_exact_costs(board, states, oracle_limits)
    report = check_samples(board, heuristic, exact_costs)
    report.update({
        "sampled_states": len(states),
        "reachable_states_discovered": discovered,
        "sample_truncated": truncated,
        "oracle_skipped": len(skipped),
        "oracle_skipped_statuses": [status for _, status in skipped],
    })
    return report
