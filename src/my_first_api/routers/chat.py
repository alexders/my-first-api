"""聊天相关的路由：SSE 流式输出。"""

from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from starlette import status

from ..services import chat as service
from ..db import get_db
from ..schemas import ConversationCreate,ConversationPublic,ConversationDetail


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/stream")
async def chat_stream():
    """以 SSE 形式逐块推送文本，前端用 EventSource 消费。"""
    return StreamingResponse(
        service.event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
@router.post("/conversations", response_model=ConversationPublic,status_code=status.HTTP_201_CREATED,)
def create_conversation(payload:ConversationCreate,db:Session =Depends(get_db)) :
    """创建一个新的对话记录"""
    conversation =service.create_conversation(db,payload)
    return conversation

@router.get("/conversations", response_model=list[ConversationPublic])
def list_conversations(db:Session =Depends(get_db)) :
    """查出所有对话，按 id 降序"""
    conversation =service.list_conversations(db)
    return conversation

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """会话详情，连同它的全部消息一起查出来。查不到返回 404。"""
    conversation = service.get_conversation_detail(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation