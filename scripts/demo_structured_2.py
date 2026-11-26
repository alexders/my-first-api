"""验证结构化输出：schema 注入 + Pydantic 校验 + 自动重试。"""

import asyncio
import logging

from my_first_api.logging_config import setup_logging
from my_first_api.services.ai import extract_expenses

setup_logging("INFO", "WARNING")
logger = logging.getLogger(__name__)

SAMPLES = [
    "昨天打车花了 38 块",
    "中午吃饭 45，晚上超市买了 120 的日用品",
    "今天心情不错",
]


async def main() -> None:
    for text in SAMPLES:
        logger.info("输入：%s", text)
        try:
            result = await extract_expenses(text)
        except ValueError as exc:
            logger.error("抽取失败：%s", exc)
            continue
        logger.info("结果：%s", result.model_dump_json(ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
