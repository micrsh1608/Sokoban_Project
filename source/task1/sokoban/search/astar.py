"""Phuong: adapt your supplied A* here. See docs/INTEGRATION.md."""
from ..core.model import Board, State
from .contracts import SearchLimits, SearchResult, Status


def solve(board: Board, initial: State, limits: SearchLimits) -> SearchResult:
    # TODO: f=g+h, best_g, parent links, stale-entry skipping, reopen when
    # a better g is found, deadline/node limit and metrics.
    return SearchResult(Status.NOT_IMPLEMENTED,
                        message="A* adapter is ready; integrate algorithm and heuristic.")
