"""
Chat conversation memory using LangChain's ChatMessageHistory.
Sessions are stored in-memory (swap for Redis/DB in production).
"""
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def clear_session(session_id: str) -> None:
    _store.pop(session_id, None)
