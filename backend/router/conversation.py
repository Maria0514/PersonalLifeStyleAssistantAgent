from fastapi import APIRouter
from typing import Annotated
from loguru import logger
from database import *

router = APIRouter(prefix="/conversations")

conversationDB = ConversationDB()
messageDB = MessageDB()

@router.get("/")
async def get_conversations():
    """
    获取对话列表
    """
    logger.info("获取对话列表")
    conversations = conversationDB.get_all_conversations()
    return {
        "conversations": conversations,
        "total": len(conversations)
    }
    
@router.get("/{session_id}/messages")
async def get_conversation_messages(session_id: str, 
                                    limit: Annotated[int, "每页消息数量"] = 50, 
                                    offset: Annotated[int, "偏移量"] = 0):
    """
    获取对话消息
    """
    logger.info(f"获取对话 {session_id} 的消息")
    messages, total = messageDB.get_messages_by_session(session_id, limit, offset)
    return {
        "messages": messages,
        "total": total,
        "has_more": offset + limit < total
    }
    
@router.delete("/{session_id}")
async def delete_conversation(session_id: str):
    """
    删除对话
    """
    logger.info(f"删除对话 {session_id}")
    conversationDB.delete_conversation(session_id)
    messageDB.delete_message_by_session(session_id)
    return {
        "success": True,
        "message": "对话已删除"
    }


@router.get("/{session_id}/search")
async def search_in_conversation(session_id: str, q: str):
    """
    会话内搜索消息
    """
    logger.info(f"搜索消息：{q}在会话{session_id}")
    messages = messageDB.search_messages(q, session_id)
    return {
        "messages": messages,
        "total": len(messages)
    }
