from collections import deque
from typing import Optional
from autogen_core.models import SystemMessage, UserMessage

from .data_types import EndUserMessage


class SessionStateManager:
    def __init__(self, history_length: int = 100):
        self.session_states = {}
        self.session_histories = {}
        self.history_length = history_length

    def set_active_agent(self, conversation_id: str, agent_type: str) -> None:
        self.session_states[conversation_id] = agent_type

    def get_active_agent(self, conversation_id: str) -> Optional[str]:
        return self.session_states.get(conversation_id)

    def clear_session(self, conversation_id: str) -> None:
        if conversation_id in self.session_states:
            del self.session_states[conversation_id]
        if conversation_id in self.session_histories:
            del self.session_histories[conversation_id]

    def add_to_history(self, conversation_id: str, message: SystemMessage | UserMessage) -> None:
        if conversation_id not in self.session_histories:
            self.session_histories[conversation_id] = deque(maxlen=self.history_length)
        self.session_histories[conversation_id].append(message)

    def get_history(self, conversation_id: str) -> deque:
        return self.session_histories.get(conversation_id, deque())
