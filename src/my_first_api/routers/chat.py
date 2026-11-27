"""聊天相关的路由：SSE 流式输出。"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from starlette import status

from ..db import get_db
from ..llm import get_llm_client
from ..schemas import ConversationCreate, ConversationDetail, ConversationPublic
from ..services import chat as service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/stream")
async def chat_stream(
    conversation_id: int,
    message: str,
    db: Session = Depends(get_db),
    client: AsyncOpenAI = Depends(get_llm_client),
):
    """流式输出模型的回答，同时把这一轮的问答存进数据库。"""
    # 先查出这个会话是否存在
    conversation = service.get_conversation_detail(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    # 下面返回一个 StreamingResponse，里面的内容是一个异步生成器
    return StreamingResponse(
        service.event_stream(conversation_id, message, client),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 的缓冲
        },
    )


@router.post(
    "/conversations",
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    """创建一个新的对话记录"""
    conversation = service.create_conversation(db, payload)
    return conversation


@router.get("/conversations", response_model=list[ConversationPublic])
def list_conversations(db: Session = Depends(get_db)):
    """查出所有对话，按 id 降序"""
    conversation = service.list_conversations(db)
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """会话详情，连同它的全部消息一起查出来。查不到返回 404。"""
    conversation = service.get_conversation_detail(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation
