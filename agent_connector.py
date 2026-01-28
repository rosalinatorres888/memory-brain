#!/usr/bin/env python3
"""
Universal Agent Connector for Memory Brain
Drop-in module for any agent to log activity to central Memory Brain.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

class AgentConnector:
    """
    Usage:
        from agent_connector import AgentConnector
        brain = AgentConnector("MyAgentName")
        brain.log("action_name", {"key": "value"})
    """
    
    DB_PATH = Path("/Users/rosalinatorres/Documents/memory-brain/central_memory.db")
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._ensure_tables()
        print(f"🧠 {agent_name} connected to Memory Brain")
    
    def _ensure_tables(self):
        """Ensure agent_activity table exists"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                status TEXT DEFAULT 'success'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                lesson_content TEXT,
                quiz_score REAL,
                study_date TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def log(self, action: str, details: dict = None, status: str = "success"):
        """Log agent action"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_activity (agent_name, action, timestamp, details, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.agent_name,
            action,
            datetime.now().isoformat(),
            json.dumps(details) if details else "",
            status
        ))
        conn.commit()
        conn.close()
    
    def log_study(self, topic: str, content: str = None, score: float = None):
        """Log study progress"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO study_progress (agent_name, topic, lesson_content, quiz_score, study_date)
            VALUES (?, ?, ?, ?, ?)
        """, (self.agent_name, topic, content, score, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def log_job(self, company: str, role: str, action: str):
        """Log job hunting activity"""
        self.log(f"job_{action}", {"company": company, "role": role})


if __name__ == "__main__":
    brain = AgentConnector("TestAgent")
    brain.log("test_action", {"test": "data"})
    print("✅ Agent Connector working!")
