"""
Chat conversation memory using LangChain's ChatMessageHistory.
Sessions are stored in-memory (swap for Redis/DB in production).
"""
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from app.core.config import settings

class LimitedChatMessageHistory(ChatMessageHistory):
    def add_message(self, message):
        super().add_message(message)
        if len(self.messages) > settings.MAX_HISTORY_LENGTH:
            self.messages = self.messages[-settings.MAX_HISTORY_LENGTH:]

    def add_messages(self, messages):
        super().add_messages(messages)
        if len(self.messages) > settings.MAX_HISTORY_LENGTH:
            self.messages = self.messages[-settings.MAX_HISTORY_LENGTH:]

_store: dict[str, LimitedChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = LimitedChatMessageHistory()
    return _store[session_id]


def clear_session(session_id: str) -> None:
    _store.pop(session_id, None)
