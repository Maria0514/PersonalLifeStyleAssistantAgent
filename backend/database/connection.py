import sqlite3
from loguru import logger
import os
DATABASE_PATH = './data.db'
logger.info(f"数据库路径: {os.path.abspath(DATABASE_PATH)}")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = (), fetch_one: bool = False):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
    except Exception as e:
        logger.info(f"数据库语句失败：{e}")
        raise
    
def execute_many(query: str, params: list):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
    except Exception as e:
        logger.info(f"批量执行数据库语句失败：{e}")
        raise