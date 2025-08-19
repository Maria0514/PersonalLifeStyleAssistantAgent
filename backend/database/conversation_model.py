from datetime import datetime
from typing import List, Dict, Optional, Any
from .connection import execute_query, get_db_connection


class ConversationDB:
    
    @staticmethod
    def get_all_conversations() -> List[dict[str, Any]]:
        
        query = """
        SELECT * FROM conversations
        ORDER BY updated_at DESC
        """
        
        rows = execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def delete_conversation(session_id: str):
        query = """
        DELETE FROM conversations WHERE session_id = ?
        """
        
        execute_query(query, (session_id,))
        
    @staticmethod
    def create_conversation(session_id: str, title: str):
        query = """
        INSERT INTO conversations (session_id, title) VALUES (?, ?)
        """
        execute_query(query, (session_id, title))
        
    @staticmethod
    def update_conversation_count(session_id: str):
        query = """
        UPDATE conversations SET message_count = message_count + 1 WHERE session_id = ?
        """
        execute_query(query, (session_id,))
        
    @staticmethod
    def has_conversation(session_id: str) -> bool:
        query = """
        SELECT COUNT(*) FROM conversations WHERE session_id = ?
        """
        result = execute_query(query, (session_id,))
        return result[0]["COUNT(*)"] > 0