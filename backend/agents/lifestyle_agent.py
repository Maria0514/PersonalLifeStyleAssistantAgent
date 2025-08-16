from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv
from pydantic import SecretStr
import os
from tools import get_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from loguru import logger
from datetime import datetime

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
silicon_flow_api_key = os.getenv("SILICON_FLOW_API_KEY")
silicon_flow_api_base = os.getenv("SILICON_FLOW_API_BASE")

current_local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

from langchain.tools import tool

@tool(description="获取当前时间")
def get_current_time() -> str:
    """返回当前时间（UTC+8）。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


system_message = f"""
你是一个友善、专业的个人生活助理AI，名叫"小助手"。你的使命是帮助用户处理日常生活事务，提供实用的建议和服务。
涉及时间问题请调用get_current_time工具，不需要联网搜索。

## 🎯 核心原则

### 1. 交流风格
- **语气平和友善**：始终保持温和、耐心的语气，像朋友一样与用户交流
- **积极正面**：即使面对困难问题，也要保持乐观和解决问题的态度
- **专业可靠**：提供准确、实用的信息和建议
- **个性化服务**：根据用户的具体需求提供定制化的帮助

### 2. 输出格式
- **必须使用 Markdown 格式**输出所有回复
- 合理使用标题、列表、加粗、代码块等 Markdown 元素
- 让回复结构清晰、易于阅读

### 3. 功能定位
你具备以下核心能力：
- 🧮 **数学计算**：帮助用户进行各种数学运算
- 🔍 **信息搜索**：搜索最新的信息、天气、新闻等
- ⏰ **提醒服务**：设置和管理用户的提醒事项
- 💡 **生活建议**：提供实用的生活小贴士和建议

"""
logger.info(f"System message initialized: {system_message}")
prompt = SystemMessage(content=system_message)

class LifestyleAgent:
    def __init__(self) -> None:
        self.tools = get_tools()
        self.model = ChatOpenAI(
            base_url = silicon_flow_api_base,
            api_key = SecretStr(silicon_flow_api_key),
            model = "Qwen/Qwen3-30B-A3B-Thinking-2507",  # 模型名称
        )
        self.memory_saver = MemorySaver()
        self.agent_executor = create_react_agent(
            self.model, 
            tools=[*self.tools] + [get_current_time], 
            verbose=True, 
            checkpointer=self.memory_saver,
            message_modifier=prompt
            )

    async def process_message(self, message: str, config: dict = None):
        message = HumanMessage(content=message)
        response = await self.agent_executor.ainvoke({"messages": [message]}, config=config)
        token_usage = self.cal_tokens(response)
        tool_usage = self.get_tool_usage(response)
        return response, token_usage, tool_usage

    def cal_tokens(self, response) -> int:
        result = 0
        for message in response['messages']:
            if isinstance(message, AIMessage):
                metadata = message.response_metadata
                result += metadata.get("token_usage").get("total_tokens")
        return result

    def get_tool_usage(self, response) -> dict:
        tool_usage = []
        for message in response['messages']:
            if isinstance(message, ToolMessage):
                tool_name = message.name
                tool_usage.append(tool_name)
        return tool_usage