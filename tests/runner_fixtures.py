"""Fault-injection controllers used ONLY by the runner tests."""
import time
from sokoban.core.model import Action


class HangAgent:
    def choose_action(self, observation, deadline):
        while True:
            time.sleep(1)


class ErrorAgent:
    def choose_action(self, observation, deadline):
        raise RuntimeError('deliberate test error')


class InvalidAgent:
    def choose_action(self, observation, deadline):
        return 'Teleport'


class SnapshotAgent:
    def choose_action(self, observation, deadline):
        # Both agents must see the unchanged first-round arena snapshot.
        assert observation.state.players == ((2, 2), (4, 10))
        assert observation.state.round_index == 0
        return Action.NORTH


class BrokenConstructor:
    def __init__(self):
        raise RuntimeError('deliberate startup failure')
