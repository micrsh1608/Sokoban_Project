"""Every solver returns this contract; GUI/experiments must not inspect heap internals."""
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from ..core.model import Action, Board, State
from ..core.rules import is_goal, replay


class Status(str, Enum):
    SOLVED = "solved"
    UNSOLVABLE = "unsolvable"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    LIMIT_REACHED = "limit_reached"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass(frozen=True)
class SearchLimits:
    seconds: float = 10.0
    max_expanded: int = 100_000

    def __post_init__(self):
        if not isfinite(self.seconds) or self.seconds <= 0 or self.max_expanded <= 0:
            raise ValueError("Search limits must be positive.")


@dataclass
class SearchMetrics:
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    max_reached: int = 0
    preprocess_ms: float = 0.0


@dataclass
class SearchResult:
    status: Status
    actions: tuple[Action, ...] = ()
    total_cost: int | None = None
    metrics: SearchMetrics = field(default_factory=SearchMetrics)
    message: str = ""


def validate_result(board: Board, initial: State, result: SearchResult):
    if result.status == Status.SOLVED:
        states = replay(board, initial, result.actions)
        if not is_goal(board, states[-1]):
            raise ValueError("Solver claimed solved but final state is not a goal.")
        if result.total_cost != len(result.actions):
            raise ValueError("Cost must equal action count under the unit-cost convention.")
    elif result.total_cost is not None or result.actions:
        raise ValueError("Non-solved results must not contain a solution/cost.")
