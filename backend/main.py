from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from datetime import datetime
from agents.lifestyle_agent import LifestyleAgent
import time

origins = [
    "http://localhost:5173",
]

app = FastAPI()
# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True  # 添加这一行
)

class UserMessage(BaseModel):
    message: str
    timestamp: str

class Metadata(BaseModel):
    tokens_used: float = 0.0
    response_time: float = 0.0
    confidence: float = 0.0

class ResponseMessage(BaseModel):
    message: str
    success: bool = True
    tool_used: list[str] = []
    metadata: Metadata = Metadata()
    

@app.post("/message")
async def receive_message(message: UserMessage):
    thread_id = f"session_{int(time.time())}"
    config = {
        "configurable":{
            "thread_id": thread_id
        }
    }
    start_time = time.perf_counter()
    
    response, token_usage, tool_usage = await LifestyleAgent().process_message(message.message, config=config)
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