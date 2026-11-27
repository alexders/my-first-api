"""验证流式响应能否拿到 token 用量。"""

import asyncio

from my_first_api.config import get_settings
from my_first_api.llm import get_llm_client


async def main() -> None:
    settings = get_settings()
    client = get_llm_client()

    stream = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": "用一句话介绍什么是 RAG"}],
        stream=True,
        stream_options={"include_usage": True},
    )

    index = 0
    async for chunk in stream:
        index += 1
        print(f"帧{index}: choices={len(chunk.choices)}  usage={chunk.usage}")
        if chunk.choices:
            piece = chunk.choices[0].delta.content
            if piece:
                print(f"    文本: {piece!r}")


if __name__ == "__main__":
    asyncio.run(main())
