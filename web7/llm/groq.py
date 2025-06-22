import os

from groq import AsyncGroq


def init_groq() -> AsyncGroq:
    groq_client = AsyncGroq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    return groq_client


async def groq_complete(
    groq_client: AsyncGroq, system_prompt: str, user_prompt: str
) -> str:
    chat_completion = await groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content
