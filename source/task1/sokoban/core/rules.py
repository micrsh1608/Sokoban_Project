"""Single-player rules shared by the UI, UCS and A*. Owner: Huy."""
from dataclasses import dataclass
from .model import Action, Board, DIRECTIONS, State, offset


@dataclass(frozen=True)
class Transition:
    action: Action
    state: State
    cost: int = 1


def step(board: Board, state: State, action: Action) -> State | None:
    if action not in DIRECTIONS:
        return None
    target = offset(state.player, action)
    if target not in board.floors:
        return None
    boxes = state.boxes
    if target in boxes:
        destination = offset(target, action)
        if destination not in board.floors or destination in boxes:
            return None
        boxes = frozenset((boxes - {target}) | {destination})
    return State(target, boxes)


def successors(board: Board, state: State):
    for action in DIRECTIONS:
        next_state = step(board, state, action)
        if next_state is not None:
            yield Transition(action, next_state)


def is_goal(board: Board, state: State) -> bool:
    return state.boxes == board.goals


def replay(board: Board, initial: State, actions) -> tuple[State, ...]:
    states = [initial]
    for index, raw_action in enumerate(actions):
        action = Action(raw_action)
        next_state = step(board, states[-1], action)
        if next_state is None:
            raise ValueError(f"Illegal action at index {index}: {action.value}")
        states.append(next_state)
    return tuple(states)
