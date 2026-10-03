"""Phuong owns this replaceable controller file."""
from ..core.model import Action
from .contracts import Observation


class AgentTwo:
    def choose_action(self, observation: Observation, deadline: float) -> Action:
        raise NotImplementedError("Implement a search-based controller with a deadline.")
