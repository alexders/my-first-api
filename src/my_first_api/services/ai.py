"""LLM 能力：结构化抽取。"""

import json
import logging

from openai import AsyncOpenAI
from pydantic import ValidationError

from ..config import get_settings
from ..llm import get_llm_client
from ..schemas import ExpenseExtraction

logger = logging.getLogger(__name__)

settings = get_settings()

_SCHEMA = json.dumps(ExpenseExtraction.model_json_schema(), ensure_ascii=False)
SYSTEM_PROMPT = (
    "你是信息抽取器，从用户的话中提取所有支出。"
    f"输出必须严格符合这个 JSON Schema：{_SCHEMA}\n"
    "只输出 JSON 对象，不要解释，不要 markdown 代码块。"
    '没有支出时返回 {"items": []}。'
)


async def extract_expenses(
    text: str, client: AsyncOpenAI | None = None, retries: int = 1
) -> ExpenseExtraction:
    """把一句话解析成结构化支出列表，校验失败时自动重试。"""
    client = client or get_llm_client()
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or ""
        try:
            result = ExpenseExtraction.model_validate_json(raw)
        except ValidationError as exc:
            last_error = exc
            logger.warning("第 %d 次校验失败：%s", attempt + 1, last_error)
            continue
        logger.info("抽取成功，%d 笔", len(result.items))
        return result
    raise ValueError(f"模型输出无法解析：{last_error}")
