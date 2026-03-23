"""
Simple conversational chain using LangChain LCEL.
History-aware multi-turn conversation with the farmer.
"""
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

from app.core.llm import get_llm
from app.prompts.templates import farmer_prompt
from app.memory.chat_history import get_session_history


def build_chat_chain():
    llm = get_llm()
    chain = farmer_prompt | llm | StrOutputParser()
    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )


# Singleton – built once on import
chat_chain = build_chat_chain()
