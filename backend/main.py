from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from datetime import datetime
from agents.lifestyle_agent import LifestyleAgent
import time, os
from database import *
from router import reminder, conversation, messages

origins = [
    "http://localhost:5173",
]
messageDB = MessageDB()
conversationDB = ConversationDB()

app = FastAPI()
# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True  # 添加这一行
)
app.include_router(reminder.router)
app.include_router(conversation.router)
app.include_router(messages.router)
class UserMessage(BaseModel):
    message: str
    timestamp: str
    session_id: str = None  # 前端传递的会话ID

class Metadata(BaseModel):
    tokens_used: float = 0.0
    response_time: float = 0.0
    confidence: float = 0.0

class ResponseMessage(BaseModel):
    message: str
    success: bool = True
    tool_used: list[str] = []
    metadata: Metadata = Metadata()
    
life_agent = LifestyleAgent()

@app.post("/message")
async def receive_message(message: UserMessage):
    thread_id = message.session_id or f"session_{int(time.time())}"
    config = {
        "configurable":{
            "thread_id": thread_id
        }
    }
    if(conversationDB.has_conversation(thread_id) is False):
        config_extract_first = {
            "configurable": {
                "thread_id": "extract_title_from_first_message"
            }
        }
        title = await life_agent.process_conversation_title(message.message, config=config_extract_first)
        logger.info(f"标题：{title['messages'][-1].content}")
        conversationDB.create_conversation(thread_id, title['messages'][-1].content)

    # 添加用户消息记录
    messageDB.add_message(thread_id, 'user', message.message, datetime.now().isoformat(), None)
    conversationDB.update_conversation_count(thread_id)
    start_time = time.perf_counter()

    logger.info(f"session id: {thread_id}")

    response, token_usage, tool_usage = await life_agent.process_message(message.message, config=config)
    logger.info(f"Received message: {message.message} at {message.timestamp}")

    end_time = time.perf_counter()
    response_time = end_time - start_time
    try:
        response = {
            "message": response['messages'][-1].content,
            "success": True,
            "tool_used": tool_usage,
            "metadata": {
                "tokens_used": token_usage,
                "response_time": response_time,
            }
        }
        # 添加新消息记录
        messageDB.add_message(thread_id, 'assistant', response['message'], datetime.now().isoformat(), tool_usage)
        conversationDB.update_conversation_count(thread_id)
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        response = {
            "message": "处理消息时出错",
            "success": False,
            "tool_used": [],
            "metadata": {
                "tokens_used": 0,
                "response_time": response_time,
            }
        }
    logger.info(f"Response: {response['message']} at {datetime.now()}, used tokens {token_usage}, response time: {response_time:.2f} seconds")
    return response

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }