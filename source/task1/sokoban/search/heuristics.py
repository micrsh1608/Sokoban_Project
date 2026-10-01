"""Phuong: implement and justify a heuristic; Manhattan/Euclidean are forbidden."""
from ..core.model import Board, State


class Heuristic:
    def __init__(self, board: Board):
        self.board = board
        # TODO: Precompute here; include preprocessing time in experiments.

    def __call__(self, state: State) -> float:
        raise NotImplementedError("Choose, implement and verify the team's heuristic.")
