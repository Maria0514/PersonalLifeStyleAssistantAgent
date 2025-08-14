from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv
from pydantic import SecretStr
import os
from tools import get_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
silicon_flow_api_key = os.getenv("SILICON_FLOW_API_KEY")
silicon_flow_api_base = os.getenv("SILICON_FLOW_API_BASE")

system_message = """
你是一个友善、专业的个人生活助理AI，名叫"小助手"。你的使命是帮助用户处理日常生活事务，提供实用的建议和服务。

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

## 📋 回复模板

### 标准回复结构：
```markdown
## 📌 [根据问题类型选择合适的图标和标题]

[友善的问候或确认]

### 🔍 [具体处理过程/分析]
[详细说明你的处理步骤]

### ✨ [结果/建议]
[清晰展示结果或建议]

### 💡 小贴士
[相关的实用建议或提醒]"""

prompt = SystemMessage(content=system_message)

class LifestyleAgent:
    def __init__(self) -> None:
        self.tools = get_tools()
        self.model = ChatOpenAI(
            base_url = silicon_flow_api_base,
            api_key = SecretStr(silicon_flow_api_key),
            model = "Qwen/Qwen3-8B",  # 模型名称
        )
        self.memory_saver = MemorySaver()
        self.agent_executor = create_react_agent(
            self.model, 
            tools=self.tools, 
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