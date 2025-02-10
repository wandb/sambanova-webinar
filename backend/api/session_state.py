from collections import deque
from typing import Optional

from .data_types import EndUserMessage


class SessionStateManager:
    def __init__(self, history_length: int = 100):
        self.session_states = {}
        self.session_histories = {}
        self.history_length = history_length

    def set_active_agent(self, session_id: str, agent_type: str) -> None:
        self.session_states[session_id] = agent_type

    def get_active_agent(self, session_id: str) -> Optional[str]:
        return self.session_states.get(session_id)

    def clear_session(self, session_id: str) -> None:
        if session_id in self.session_states:
            del self.session_states[session_id]
        if session_id in self.session_histories:
            del self.session_histories[session_id]

    def add_to_history(self, session_id: str, message: EndUserMessage) -> None:
        if session_id not in self.session_histories:
            self.session_histories[session_id] = deque(maxlen=self.history_length)
        self.session_histories[session_id].append(message)

    def get_history(self, session_id: str) -> deque:
        return self.session_histories.get(session_id, deque())
