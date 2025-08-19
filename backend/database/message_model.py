from typing import Dict, List, Any, Tuple
from .connection import execute_query

class MessageDB():
    @staticmethod
    def get_messages_count_by_session(session_id: str) -> int:
        query = """
        SELECT COUNT(*) FROM messages
        WHERE session_id = ?
        """
        result = execute_query(query, (session_id,))
        return result[0]["COUNT(*)"] if result else 0
    
    @staticmethod
    def get_messages_by_session(session_id: str, limit: int, offset: int) -> Tuple[List[Dict[str, Any]], int]:
        # 这里是获取消息的逻辑
        query = """
        SELECT * FROM messages
        WHERE session_id = ?
        LIMIT ? OFFSET ?
        """
        total = MessageDB.get_messages_count_by_session(session_id)
        return execute_query(query, (session_id, limit, offset)), total
    
    @staticmethod
    def delete_message_by_session(session_id: str):
        """
        根据session_id删除消息记录
        """
        query = """
        DELETE FROM messages WHERE session_id = ?
        """
        
        execute_query(query, (session_id,))

    @staticmethod
    def search_messages(q: str, session_id: str = None) -> List[Dict[str, Any]]:
        query = """
        SELECT * FROM messages WHERE content LIKE ?
        """
        params = [f"%{q}%"]
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        return execute_query(query, params)
    
    @staticmethod
    def add_message(session_id: str, role: str, content: str, timestamp: str, tool_usage: list[str]):
        query = """
        INSERT INTO messages (session_id, role, content, timestamp, tool_used)
        VALUES (?, ?, ?, ?, ?)
        """
        if tool_usage is None:
            tool_usage = []
        execute_query(query, (session_id, role, content, timestamp, ','.join(tool_usage)))

