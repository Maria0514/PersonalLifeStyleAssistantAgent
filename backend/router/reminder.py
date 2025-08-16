from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
import sqlite3
from datetime import datetime, timedelta
from loguru import logger

router = APIRouter(prefix="/reminders", tags=["reminder"])

class Reminder(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "complete"]
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    

@router.get("/upcoming")
async def get_upcoming_reminders(minutes_ahead: int = 5):
    # 这里是获取即将到期的提醒的逻辑
    due_time = datetime.now() + timedelta(minutes=minutes_ahead)
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, due_date, priority, status, created_at, updated_at, completed_at FROM reminders WHERE due_date <= ? AND status = ?", (due_time, "pending"))
    rows = cursor.fetchall()
    conn.close()
    
    # 将元组转换为字典格式
    upcoming_reminders = [Reminder(**dict(row)) for row in rows]
    
    return {
        "upcoming": upcoming_reminders,
        "count": len(upcoming_reminders),
        "total_upcoming": len(upcoming_reminders)
        }
    
@router.post("/{reminder_id}/complete")
async def complete_reminder(reminder_id: int):
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET status = ?, completed_at = ? WHERE id = ?", ("complete", datetime.now(), reminder_id))
    reminder = cursor.execute("SELECT id, title, status, completed_at FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
    if(reminder is None):
        return {
            "success": False,
            "error": "提醒不存在或已完成",
            "error_code": "REMINDER_NOT_FOUND"
        }
    conn.commit()
    conn.close()
    return {
        "success": True,
        "message": "提醒已标记为完成",
        "reminder": {
            "id": reminder[0],
            "title": reminder[1],
            "status": reminder[2],
            "completed_at": reminder[3]
        }
    }

@router.post("/{reminder_id}/snooze")
async def snooze_reminder(reminder_id:int, minutes:timedelta = timedelta(minutes=10)):
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
    reminder = Reminder(**dict(cursor.fetchone()))
    if(reminder is None):
        return {
            "success": False,
            "error": "提醒不存在或已完成",
            "error_code": "REMINDER_NOT_FOUND"
        }
    current_due = reminder.due_date
    new_due = current_due + minutes
    cursor.execute("UPDATE reminders SET due_date = ? WHERE id = ?", (new_due, reminder_id))

    conn.commit()
    conn.close()
    return {
        "success": True,
        "message": f"提醒已延后 {minutes} 分钟",
        "reminder": {
            "id": reminder.id,
            "title": reminder.title,
            "status": reminder.status,
            "due_date": reminder.due_date
        }
    }