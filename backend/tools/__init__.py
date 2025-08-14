from .calculator import calculator_tool

AVAILABLE_TOOLS = {
    "calculator": calculator_tool
}

def get_tools():
    return list(AVAILABLE_TOOLS.values())