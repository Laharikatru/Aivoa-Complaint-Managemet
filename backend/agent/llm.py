import os
from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma2-9b-it")


def get_llm(model: str | None = None, temperature: float = 0.2):
    """ChatGroq client bound to the configured model (gemma2-9b-it by default per spec).
    Pass model="llama-3.3-70b-versatile" when a task needs more reasoning headroom
    (e.g. root-cause analysis over a longer complaint history)."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=model or GROQ_MODEL,
        temperature=temperature,
    )
