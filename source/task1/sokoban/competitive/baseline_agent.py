"""Explicit testing opponent, not Phuong's completed AgentTwo."""
from ..core.model import Action


class WaitAgent:
    def choose_action(self, observation, deadline):
        return Action.WAIT
