from openai import OpenAI

from app.core.config import settings
from app.services.llm.prompts import SYSTEM_PROMPT


class ResponseGenerator:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, question: str, context: str) -> str:
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
        )
        return response.choices[0].message.content or ""
