from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, Any, Annotated
import re

class CalculatorInput(BaseModel):
    """定义计算器输入的模型，包括数学表达式字符串。"""
    expression: str = Field(
        description="数学表达式字符串，如 '15 + 23' 或 '100 * 0.8'",
        examples=["15 + 23", "100 * 0.8", "(50 - 5) / 9"]
    )

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """
    用于执行基本数学计算的工具。
    输入: 数学表达式字符串，如 "15 + 23" 或 "100 * 0.8"
    输出: 计算结果
    支持: 加法(+)、减法(-)、乘法(*)、除法(/)、括号()
    """    
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str, run_manager: Optional[Any] = None) -> str:
        try:
            if not self._is_valid_expression(expression):
                return "无效的数学表达式。请确保输入正确。"
            result = self._safe_calculate(expression)
            return f"计算结果：{result}"
        except ZeroDivisionError as e:
            return f"计算错误：除数不能为零。"
        except Exception as e:
            return f"计算错误：{str(e)}"
        
    async def _arun(self, expression: str, run_manager: Optional[Any] = None) -> str:
        return self._run(expression, run_manager=run_manager)
    
    def _is_valid_expression(self, expression: str) -> bool:
        """检查表达式是否包含无效字符。"""
        allowed_chars = re.compile(r'^[0-9+\-*/().\s]+$')
        return bool(allowed_chars.match(expression))
    
    def _safe_calculate(self, expression: str) -> float:
        """安全计算表达式"""
        expression = expression.replace(' ', '')
        
        # 使用ast.literal_eval
        try:
            result = eval(expression, {"__builtins__": {}})
            return result;
        except:
            raise ValueError("无效的数学表达式")

calculator_tool = CalculatorTool()

