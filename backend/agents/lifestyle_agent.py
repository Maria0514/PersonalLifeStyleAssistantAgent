from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
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

class LifestyleAgent:
    def __init__(self) -> None:
        self.tools = get_tools()
        self.model = ChatOpenAI(
            base_url = silicon_flow_api_base,
            api_key = SecretStr(silicon_flow_api_key),
            model = "Qwen/Qwen3-8B",  # 模型名称
        )
        self.memory_saver = MemorySaver()
        self.agent_executor = create_react_agent(self.model, tools=self.tools, verbose=True, checkpointer=self.memory_saver)

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