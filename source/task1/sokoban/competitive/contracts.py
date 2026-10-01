"""Proposed competition contract; not a supplied lecturer protocol."""
from dataclasses import dataclass
from typing import Protocol
from ..core.model import Action, Board, Position


@dataclass(frozen=True)
class Box:
    id: int  # Stable across movement; single-player states do NOT need IDs.
    position: Position
    owner: int | None = None  # 0 / 1; None when off-goal or initially neutral.


@dataclass(frozen=True)
class CompetitionState:
    players: tuple[Position, Position]
    boxes: tuple[Box, ...]
    round_index: int
    max_rounds: int


@dataclass(frozen=True)
class Observation:
    board: Board
    state: CompetitionState
    agent_id: int


class Agent(Protocol):
    def choose_action(self, observation: Observation, deadline: float) -> Action:
        """deadline is an absolute time.perf_counter() timestamp in worker process."""
        ...
