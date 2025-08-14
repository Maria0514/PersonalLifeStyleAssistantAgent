from .calculator import calculator_tool
from .search_online import search_online_tool
from .reminders import add_reminder_tool, query_reminder_tool, update_reminder_tool


AVAILABLE_TOOLS = {
    "calculator": calculator_tool,
    "search_online": search_online_tool,
    "add_reminder": add_reminder_tool,
    "query_reminder": query_reminder_tool,
    "update_reminder": update_reminder_tool
}

def get_tools():
    return list(AVAILABLE_TOOLS.values())