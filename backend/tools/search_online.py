from langchain.tools import BaseTool
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

class SearchOnlineTool(BaseTool):
    name: str = "search_online"
    description: str = """
    实现在线搜索功能，支持天气查询、新闻搜索等
    """

    def _run(self, query: str) -> str:
        search = TavilySearchResults(max_results=5)
        result = search.invoke(query)
        return result

search_online_tool = SearchOnlineTool()