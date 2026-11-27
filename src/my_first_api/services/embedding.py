"""文本向量化：把消息内容转成 1024 维向量。"""

import logging

from openai import AsyncOpenAI

from ..llm import get_llm_client

logger = logging.getLogger(__name__)

EMBED_MODEL = "text-embedding-v3"
"""批量向量化。失败时整体降级为 None，不抛异常打断主流程。"""


async def embed_texts(
    texts: list[str], client: AsyncOpenAI | None = None
) -> list[float]:
    if not texts:
        return []
    cli = client or get_llm_client()
    try:
        res = await cli.embeddings.create(model=EMBED_MODEL, input=texts)
    except Exception:
        logger.exception("向量化失败，%d 条文本不存向量", len(texts))
        return [None] * len(texts)
        # 按 index 排序，保证返回顺序和输入顺序一致
    return [item.embedding for item in sorted(res.data, key=lambda x: x.index)]


"""单条文本向量化。"""


async def embed_text(text: str, client: AsyncOpenAI | None) -> list[float] | None:
    result = await embed_texts([text], client)
    return result[0] if result else None
