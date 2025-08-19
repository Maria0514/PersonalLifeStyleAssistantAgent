from fastapi import APIRouter
from typing import Optional
from loguru import logger
from database import *

router = APIRouter(prefix="/messages", tags=["message"])

conversationDB = ConversationDB()
messageDB = MessageDB()

@router.get("/search")
async def search_messages(q: str, session_id: Optional[str] = None):
    logger.info(f"搜索消息: {q}, 会话ID: {session_id}")
    messages = messageDB.search_messages(q, session_id)
    return {
        "messages": messages,
        "total": len(messages)
    }