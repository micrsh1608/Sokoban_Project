"""Atomic joint transitions. Both intents use the SAME immutable snapshot.

See docs/DECISIONS.md for the team's conservative collision conventions.
"""
from dataclasses import dataclass
from ..core.model import Action, Layout, Position, offset
from .contracts import Box, CompetitionState


@dataclass(frozen=True)
class TurnResult:
    state: CompetitionState
    actions: tuple[Action, Action]
    moved: tuple[bool, bool]
    reasons: tuple[str, str]


@dataclass(frozen=True)
class _Intent:
    player_to: Position
    box_id: int | None = None
    box_to: Position | None = None

    def destinations(self) -> frozenset[Position]:
        return frozenset({self.player_to} if self.box_to is None
                         else {self.player_to, self.box_to})


class CompetitionEngine:
    def __init__(self, layout: Layout, rounds: int):
        if len(layout.players) != 2 or type(rounds) is not int or rounds <= 0:
            raise ValueError("Competition requires two players and a positive integer n.")
        self.board = layout.board
        if self.board.floors & self.board.walls or not self.board.goals <= self.board.floors:
            raise ValueError("Invalid board floors/walls/goals.")
        if not layout.boxes or len(layout.boxes) != len(self.board.goals):
            raise ValueError("Team convention: equal nonzero boxes and goals.")
        self.max_rounds = rounds
        self.initial = CompetitionState(
            (layout.players[0], layout.players[1]),
            tuple(Box(i, p) for i, p in enumerate(sorted(layout.boxes))), 0, rounds)
        self._box_ids = frozenset(box.id for box in self.initial.boxes)
        self.validate_state(self.initial)

    def validate_state(self, state: CompetitionState) -> None:
        if (type(state.round_index) is not int or type(state.max_rounds) is not int
                or state.max_rounds != self.max_rounds
                or not 0 <= state.round_index <= self.max_rounds):
            raise ValueError("Invalid round index or maximum rounds.")
        if len(state.players) != 2 or len(set(state.players)) != 2:
            raise ValueError("Players must occupy distinct cells.")
        if any(p not in self.board.floors for p in state.players):
            raise ValueError("A player is outside playable floors.")
        ids = [box.id for box in state.boxes]
        positions = [box.position for box in state.boxes]
        if (any(type(i) is not int for i in ids) or len(ids) != len(set(ids))
                or frozenset(ids) != self._box_ids):
            raise ValueError("Box identities must be preserved and unique.")
        if len(positions) != len(set(positions)):
            raise ValueError("Boxes cannot overlap.")
        if set(positions) & set(state.players):
            raise ValueError("Players cannot overlap boxes.")
        for box in state.boxes:
            if box.position not in self.board.floors:
                raise ValueError("A box is outside playable floors.")
            if box.owner is not None and (type(box.owner) is not int or box.owner not in (0, 1)):
                raise ValueError("Owner must be None, 0 or 1.")
            if box.owner is not None and box.position not in self.board.goals:
                raise ValueError("An off-goal box must be neutral.")

    def scores(self, state: CompetitionState) -> tuple[int, int]:
        self.validate_state(state)
        return tuple(sum(box.owner == agent and box.position in self.board.goals
                         for box in state.boxes) for agent in (0, 1))

    def finished(self, state: CompetitionState) -> bool:
        self.validate_state(state)
        return state.round_index == state.max_rounds

    def winner(self, state: CompetitionState) -> int | None:
        """Only valid after n rounds: 0/1 wins; None means a draw."""
        if not self.finished(state):
            raise ValueError("Determine winner only after n rounds.")
        a, b = self.scores(state)
        return None if a == b else (0 if a > b else 1)

    def _intent(self, state, agent, action, boxes_by_position):
        if action == Action.WAIT:
            return None, "wait"
        target = offset(state.players[agent], action)
        other = state.players[1 - agent]
        if target not in self.board.floors:
            return None, "blocked_wall_or_void"
        if target == other:
            return None, "blocked_player"
        box = boxes_by_position.get(target)
        if box is None:
            return _Intent(target), "moved"
        destination = offset(target, action)
        if destination not in self.board.floors:
            return None, "blocked_box_wall_or_void"
        if destination == other:
            return None, "blocked_box_player"
        if destination in boxes_by_position:
            return None, "blocked_box_box"
        return _Intent(target, box.id, destination), "pushed"

    def resolve(self, state: CompetitionState, actions) -> TurnResult:
        """Resolve two intents, then commit once. Invalid action values become Wait.

        Malformed pairs, corrupt states and calls after the end raise ValueError.
        actions in the result are normalized requests; reasons/moved say what ran.
        """
        self.validate_state(state)
        if state.round_index == state.max_rounds:
            raise ValueError("Match is finished; no additional round allowed.")
        if not isinstance(actions, (tuple, list)) or len(actions) != 2:
            raise ValueError("Supply exactly two actions.")
        normalized, intents, reasons = [], [], []
        boxes_by_position = {box.position: box for box in state.boxes}
        for agent, raw in enumerate(actions):
            try:
                action = Action(raw)
            except (TypeError, ValueError):
                normalized.append(Action.WAIT)
                intents.append(None)
                reasons.append("invalid_action")
                continue
            normalized.append(action)
            intent, reason = self._intent(state, agent, action, boxes_by_position)
            intents.append(intent)
            reasons.append(reason)
        first, second = intents
        if first is not None and second is not None:
            same_box = first.box_id is not None and first.box_id == second.box_id
            overlapping = bool(first.destinations() & second.destinations())
            if same_box or overlapping:
                intents = [None, None]
                reason = "conflict_same_box" if same_box else "conflict_destination"
                reasons = [reason, reason]
        # No intermediate update was exposed to either intent above.
        players = list(state.players)
        moved_boxes = {}
        for agent, intent in enumerate(intents):
            if intent is not None:
                players[agent] = intent.player_to
                if intent.box_id is not None:
                    owner = agent if intent.box_to in self.board.goals else None
                    moved_boxes[intent.box_id] = Box(intent.box_id, intent.box_to, owner)
        boxes = tuple(moved_boxes.get(box.id, box) for box in state.boxes)
        next_state = CompetitionState(tuple(players), boxes, state.round_index + 1, state.max_rounds)
        self.validate_state(next_state)
        return TurnResult(next_state, tuple(normalized),
                          tuple(intent is not None for intent in intents), tuple(reasons))

    def step(self, state: CompetitionState,
             actions: tuple[Action, Action]) -> CompetitionState:
        """Preserve the scaffold's State -> State interface."""
        return self.resolve(state, actions).state
