"""最小可跑的 LLM 调用：验证 key、网络、计费信息。"""

import logging
import time

from openai import OpenAI

from my_first_api.config import get_settings
from my_first_api.logging_config import setup_logging

setup_logging("INFO")
logger = logging.getLogger(__name__)
settings = get_settings()

client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    timeout=30,
)

start = time.perf_counter()
resp = client.chat.completions.create(
    model=settings.llm_model,
    messages=[
        {"role": "system", "content": "你是一个简洁的中文助手，回答不超过 50 字。"},
        {"role": "user", "content": "用一句话解释什么是向量数据库"},
    ],
    temperature=0.3,
    max_tokens=200,
)
cost = time.perf_counter() - start

logger.info("回答：%s", resp.choices[0].message.content)
logger.info("用量：%s", resp.usage)
logger.info("耗时：%.2fs", cost)
