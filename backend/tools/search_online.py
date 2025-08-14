from langchain.tools import BaseTool
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

class SearchOnlineTool(BaseTool):
    name: str = "search_online"
    description: str = """
    在线搜索工具，用于获取实时信息，包括：
    - 天气查询
    - 新闻搜索  
    - **当前日期时间** ← 添加这个
    - 实时数据查询
    
    当用户询问"今天几号"、"现在几点"等时间问题时，也应该使用此工具获取准确信息。
    """

    def _run(self, query: str) -> str:
        search = TavilySearchResults(max_results=5)
        result = search.invoke(query)
        return result

search_online_tool = SearchOnlineTool()