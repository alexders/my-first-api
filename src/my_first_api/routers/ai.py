"""AI 能力相关接口：结构化抽取。"""

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI

from ..llm import get_llm_client
from ..schemas import ExpenseExtraction, ExtractRequest
from ..services import ai as ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/extract", response_model=ExpenseExtraction)
async def extract_expenses(
    payload: ExtractRequest, client: AsyncOpenAI = Depends(get_llm_client)
):
    """把一段自然语言解析成结构化支出列表。"""
    try:
        return await ai_service.extract_expenses(payload.text, client)
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail="模型输出无法解析为结构化数据，请重试"
        ) from exc
