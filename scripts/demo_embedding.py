"""独立验证 embedding 接口：连通性 + 真实维度。"""

import asyncio
import logging

from my_first_api.config import get_settings
from my_first_api.llm import get_llm_client
from my_first_api.logging_config import setup_logging


async def main() -> None:
    logger = logging.getLogger(__name__)
    settings = get_settings()
    setup_logging(settings.log_level, "INFO" if settings.debug else "WARNING")
    client = get_llm_client()
    res = await client.embeddings.create(
        model="text-embedding-v3", input=["我昨天中午吃饭花了45块", "今天天气不错"]
    )
    for item in res.data:
        logger.info(
            f"第 {item.index} 条 -> 维度 {len(item.embedding)}，前三位 {item.embedding[:3]}"
        )

    logger.info(f"用量：{res.usage.total_tokens} tokens")


if __name__ == "__main__":
    asyncio.run(main())
