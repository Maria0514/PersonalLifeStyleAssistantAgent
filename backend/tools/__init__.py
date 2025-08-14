from .calculator import calculator_tool
from .search_online import search_online_tool


AVAILABLE_TOOLS = {
    "calculator": calculator_tool,
    "search_online": search_online_tool
}

def get_tools():
    return list(AVAILABLE_TOOLS.values())