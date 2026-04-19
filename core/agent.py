from core.state import AgentState


class ACEAgent:
    def _init__(self, max_steps=10):
        self.max_steps = max_steps
        self.state = AgentState()
