import ollama
from typing import Generator
from ..config import settings

SYSTEM_PROMPT = """
You are an advanced AI assistant tasked with generating detailed, accurate answers based solely on the provided context...
### Important:
- Restrict your answers to the context provided.
- Do not include external knowledge, assumptions, or irrelevant information.
"""

def answer_from_context(context: str, question: str) -> str:
    # Aggregate streamed chunks into a single string response
    chunks = []
    for part in ollama.chat(
        model=settings.CHAT_MODEL,
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"},
        ],
    ):
        if part.get("done") is False:
            chunks.append(part["message"]["content"])
        else:
            break
    return "".join(chunks)
