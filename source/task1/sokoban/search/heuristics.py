"""Heuristic for Sokoban A*.

The heuristic is based on shortest paths on the static floor graph.  It does
not use Manhattan or Euclidean distance.
"""
from collections import deque
from ..core.model import Board, Position, State


class Heuristic:
    """Sum of each box's nearest-goal floor-graph distance.

    Boxes and other boxes are ignored while building the static graph.  This
    makes the value a lower bound on the number of pushes, and therefore also
    a lower bound on the total number of actions.
    """

    def __init__(self, board: Board):
        self.board = board
        self._goal_distances = {
            goal: self._bfs_from_goal(goal) for goal in board.goals
        }

    def _bfs_from_goal(self, goal: Position) -> dict[Position, int]:
        distances = {goal: 0}
        queue = deque([goal])
        while queue:
            current = queue.popleft()
            r, c = current
            for neighbor in ((r - 1, c), (r + 1, c),
                             (r, c - 1), (r, c + 1)):
                if neighbor in self.board.floors and neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def _box_distance(self, box: Position) -> int:
        best = None
        for distances in self._goal_distances.values():
            value = distances.get(box)
            if value is not None and (best is None or value < best):
                best = value
        # A floor component with no goal can never move a box to a goal.
        # Contribution 0 keeps the heuristic finite and remains admissible.
        return 0 if best is None else best

    def minimum_push_distance(self, boxes) -> float:
        """Lower bound for moving at least one box toward a goal."""
        return float(min((self._box_distance(box) for box in boxes), default=0))

    def __call__(self, state: State) -> float:
        return float(sum(self._box_distance(box) for box in state.boxes))
