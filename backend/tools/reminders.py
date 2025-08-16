from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel
from datetime import datetime
from typing import Type, Optional, Any, Annotated, Literal
from loguru import logger

class ReminderInput(BaseModel):
    title: Annotated[str | None, "提醒标题"] = None
    description: Annotated[str | None, "提醒描述"] = None
    due_date: Annotated[datetime | None, "截止日期"] = None
    priority: Annotated[Literal["low", "medium", "high"] | None, "优先级"] = "low"  # 默认优先级为低

class AddReminderInput(ReminderInput):
    created_at: Annotated[datetime, "创建时间"] = datetime.now()  # 新增时自动设置创建时间
    updated_at: Annotated[datetime, "更新时间"] = datetime.now()   # 新增时自动设置更新时间

    
class QueryReminderInput(ReminderInput):
    status: Annotated[Literal["pending", "complete"] | None, "状态"] = None
    start_time: Annotated[datetime | None, "查询范围开始时间"] = None
    end_time: Annotated[datetime | None, "查询范围结束时间"] = None
    priority: Annotated[Literal["low", "medium", "high"] | None, "优先级"] = None
    
class UpdateReminderInput(ReminderInput):
    id: Annotated[int, "提醒ID"]
    status: Annotated[Literal["pending", "complete"] | None, "状态"] = None
    updated_at: Annotated[datetime, "更新时间"] = datetime.now()

class AddReminderTool(BaseTool):
    name: str = "add_reminder_tool"
    description: str = """
    增加新提醒的工具，用于新增用户提醒和日程
    使用前先调用get_current_time工具获取当前时间
    使用时请确保提供必要的提醒信息，如标题、截止时间等。
    id为自增序列，无需传入
    """
    args_schema: Type[AddReminderInput] = AddReminderInput

    def __init__(self):
        super().__init__()
        self._db = SQLDatabase.from_uri("sqlite:///./data.db")

    def _run(self, **kwargs):
        logger.info(f"当前时间：{datetime.now()}")
        input = self.args_schema(**kwargs)
        query = f"""
INSERT INTO reminders (title, description, due_date, priority, status, created_at, updated_at) VALUES(
    '{input.title}', '{input.description}', '{input.due_date}', '{input.priority}', 'pending', '{input.created_at}', '{input.updated_at}'
)
"""
        logger.info(f"添加：{query}")
        self._db.run(query)
        return f"Reminder '{input.title}' added successfully."
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

class QueryReminderTool(BaseTool):
    name: str = "query_reminder_tool"
    description: str = """
    查询用户提醒和日程的工具
    使用时请提供必要的查询条件，如状态、截止时间等。
    如果用户需要某一段时间内的提醒，可以提供开始时间和结束时间。
    """
    args_schema: Type[QueryReminderInput] = QueryReminderInput
    def __init__(self):
        super().__init__()
        self._db = SQLDatabase.from_uri("sqlite:///./data.db")

    def _run(self, **kwargs):
        input = self.args_schema(**kwargs)
        query = f"""
        SELECT * FROM reminders WHERE 1=1
        """
        if input.status:
            query += f" AND status = '{input.status}'"
        if input.start_time:
            query += f" AND due_date >= '{input.start_time}'"
        if input.end_time:
            query += f" AND due_date <= '{input.end_time}'"
        if input.title:
            query += f" AND title LIKE '%{input.title}%'"
        if input.priority:
            query += f" AND priority = '{input.priority}'"
        logger.info(f"查询：{query}")

        return self._db.run(query)
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)
    
class UpdateReminderTool(BaseTool):
    name: str = "update_reminder_tool"
    description: str = """
    更新用户提醒和日程的工具
    使用前请先调用AddReminderTool工具获取要更新的提醒ID。
    使用时请提供必要的更新信息，如提醒ID、标题、截止时间等。
    """
    args_schema: Type[UpdateReminderInput] = UpdateReminderInput
    def __init__(self):
        super().__init__()
        self._db = SQLDatabase.from_uri("sqlite:///./data.db")
    def _run(self, **kwargs):
        input = self.args_schema(**kwargs)
        query = f"""
        UPDATE reminders SET
        """
        if input.title:
            query += f" title = '{input.title}',"
        if input.description:
            query += f" description = '{input.description}',"
        if input.due_date:
            query += f" due_date = '{input.due_date}',"
        if input.priority:
            query += f" priority = '{input.priority}',"
        if input.status:
            query += f" status = '{input.status}',"

        query += f" updated_at = '{input.updated_at}',"
        query = query.rstrip(",")  # 去掉最后一个逗号
        query += f" WHERE id = {input.id}"
        logger.info(f"更新：{query}")
        self._db.run(query)
        return f"Reminder '{input.title}' updated successfully."
    
    async def _arun(self, **kwargs):
        return self._run(**kwargs)

add_reminder_tool = AddReminderTool()
query_reminder_tool = QueryReminderTool()
update_reminder_tool = UpdateReminderTool()