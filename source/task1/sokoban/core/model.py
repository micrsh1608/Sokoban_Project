"""Shared data contracts. Coordinates are (row, column), never (x, y)."""
from dataclasses import dataclass
from enum import Enum

Position = tuple[int, int]


class Action(str, Enum):
    NORTH = "North"
    EAST = "East"
    WEST = "West"
    SOUTH = "South"
    WAIT = "Wait"  # Competitive extension only; never a single-player successor.


DELTAS = {
    Action.NORTH: (-1, 0), Action.EAST: (0, 1),
    Action.WEST: (0, -1), Action.SOUTH: (1, 0), Action.WAIT: (0, 0),
}
DIRECTIONS = (Action.NORTH, Action.EAST, Action.WEST, Action.SOUTH)


def offset(pos: Position, action: Action) -> Position:
    dr, dc = DELTAS[action]
    return pos[0] + dr, pos[1] + dc


@dataclass(frozen=True)
class Board:
    width: int
    height: int
    walls: frozenset[Position]
    floors: frozenset[Position]
    goals: frozenset[Position]


@dataclass(frozen=True)
class State:
    player: Position
    boxes: frozenset[Position]


@dataclass(frozen=True)
class Layout:
    board: Board
    players: tuple[Position, ...]
    boxes: frozenset[Position]

    def single_state(self) -> State:
        if len(self.players) != 1:
            raise ValueError("Single-player mode requires exactly one A.")
        return State(self.players[0], self.boxes)
