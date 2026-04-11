import os
from functools import lru_cache
from langchain_ollama import ChatOllama


@lru_cache(maxsize=1)
def get_llm():
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )