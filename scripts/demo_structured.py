"""验证结构化输出：让模型返回能被 Pydantic 解析的 JSON。"""

import logging
from openai import OpenAI

from my_first_api.config import get_settings
from my_first_api.logging_config import setup_logging

setup_logging("INFO", "WARNING")
logger = logging.getLogger(__name__)

settings = get_settings()
client = OpenAI(
    api_key=settings.llm_api_key, base_url=settings.llm_base_url, timeout=30
)

SYSTEM_PROMPT = (
    "你是信息抽取器。从用户的话里提取**所有**支出，每条包含金额、类别、备注。"
    '只输出 JSON 对象，格式为 {"items": [...]}，不要解释，不要 markdown 代码块。'
    '没有支出时返回 {"items": []}。'
)


def extract_items(text: str) -> str:
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content


for text in [
    "昨天打车花了 38 块",
    "中午吃饭 45，晚上超市买了 120 的日用品",
    "今天心情不错",
]:
    logger.info("输入：%s", text)
    raw = extract_items(text)
    logger.info("原始输出：%s", raw)
