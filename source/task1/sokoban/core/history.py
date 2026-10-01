"""Snapshot replay. Moving backward does not execute an inverse game action."""
from .model import State


class History:
    def __init__(self, states: tuple[State, ...]):
        if not states:
            raise ValueError("History must include the initial state.")
        self.states = list(states)
        self.index = 0

    @property
    def current(self) -> State:
        return self.states[self.index]

    def forward(self):
        self.index = min(self.index + 1, len(self.states) - 1)

    def backward(self):
        self.index = max(0, self.index - 1)

    def append(self, state: State):
        del self.states[self.index + 1:]
        self.states.append(state)
        self.index += 1
