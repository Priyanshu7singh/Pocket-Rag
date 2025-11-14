"""
Simple SQLite-based chat history storage
Persists chat conversations across sessions
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "chat_history.db"

def init_db():
    """Initialize chat history database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_name TEXT NOT NULL,
            user_message TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_chat(collection_name, user_message, assistant_response, context=""):
    """Save a single conversation turn"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO conversations (collection_name, user_message, assistant_response, context)
            VALUES (?, ?, ?, ?)
        """, (collection_name, user_message, assistant_response, context))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save chat: {str(e)}")
        return False

def get_conversation_history(collection_name, limit=50):
    """Get chat history for a specific collection"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT user_message, assistant_response, context, timestamp 
            FROM conversations 
            WHERE collection_name = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (collection_name, limit))
        results = c.fetchall()
        conn.close()
        
        # Reverse to show oldest first
        return list(reversed(results))
    except Exception as e:
        print(f"[ERROR] Failed to get chat history: {str(e)}")
        return []

def get_all_collections():
    """Get list of all collections that have been chatted with"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT collection_name 
            FROM conversations 
            ORDER BY MAX(timestamp) DESC
        """)
        results = c.fetchall()
        conn.close()
        return [r[0] for r in results]
    except Exception as e:
        print(f"[ERROR] Failed to get collections: {str(e)}")
        return []

def clear_collection_history(collection_name):
    """Delete chat history for a specific collection"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM conversations WHERE collection_name = ?", (collection_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to clear history: {str(e)}")
        return False
