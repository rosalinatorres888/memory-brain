#!/usr/bin/env python3
"""
Memory Brain Connector - Universal integration for all agents
Add this to any agent to enable Memory Brain logging

Usage in any agent:
    import sys
    sys.path.insert(0, os.path.expanduser("~/Documents/memory-brain"))
    from brain_connector import BrainConnector, log, learn
    
    # Quick logging
    log("MyAgent", "action", "details")
    
    # Or full connector
    brain = BrainConnector()
    brain.log_activity("MyAgent", "started", "Agent initialized")
"""

import sqlite3
import os
from datetime import datetime
from functools import wraps

class BrainConnector:
    """Universal Memory Brain connector for any agent"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.db_path = os.path.expanduser("~/Documents/memory-brain/central_memory.db")
        self._ensure_tables()
        self._initialized = True
        print(f"🧠 Brain Connector online: {self.db_path}")
        
    def _ensure_tables(self):
        """Ensure required tables exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agent sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_end DATETIME,
                actions_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        """)
        
        # Learning logs table (for ML agents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                topic TEXT,
                content TEXT,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    def log_activity(self, agent_name: str, action: str, details: str = None, status: str = "success"):
        """Log an agent activity to Memory Brain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_activity (agent_name, action, details, status, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (agent_name, action, details, status))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ Brain logging failed: {e}")
            return False
    
    def start_session(self, agent_name: str) -> int:
        """Start a new agent session, returns session_id"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_sessions (agent_name, session_start, status)
                VALUES (?, datetime('now'), 'running')
            """, (agent_name,))
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.log_activity(agent_name, "session_started", f"Session {session_id}")
            return session_id
        except Exception as e:
            print(f"⚠️ Session start failed: {e}")
            return -1
    
    def end_session(self, session_id: int, agent_name: str):
        """End an agent session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agent_sessions 
                SET session_end = datetime('now'), status = 'completed'
                WHERE id = ?
            """, (session_id,))
            conn.commit()
            conn.close()
            
            self.log_activity(agent_name, "session_ended", f"Session {session_id}")
        except Exception as e:
            print(f"⚠️ Session end failed: {e}")
    
    def log_learning(self, agent_name: str, topic: str, content: str, source: str = "ollama"):
        """Log a learning event (for study agents)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_logs (agent_name, topic, content, source, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (agent_name, topic, content[:2000] if content else "", source))
            conn.commit()
            conn.close()
            
            self.log_activity(agent_name, "learned", f"Topic: {topic}")
            return True
        except Exception as e:
            print(f"⚠️ Learning log failed: {e}")
            return False
    
    def get_recent_activity(self, agent_name: str = None, limit: int = 10):
        """Get recent agent activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent_name:
            cursor.execute("""
                SELECT agent_name, action, details, timestamp
                FROM agent_activity
                WHERE agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_name, limit))
        else:
            cursor.execute("""
                SELECT agent_name, action, details, timestamp
                FROM agent_activity
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_stats(self):
        """Get Memory Brain statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count by table
        for table in ['agent_activity', 'agent_sessions', 'learning_logs', 'tasks', 'job_applications', 'linkedin_insights']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        # Active agents (last 24 hours)
        try:
            cursor.execute("""
                SELECT DISTINCT agent_name FROM agent_activity
                WHERE timestamp > datetime('now', '-1 day')
            """)
            stats['active_agents_24h'] = [r[0] for r in cursor.fetchall()]
        except:
            stats['active_agents_24h'] = []
        
        conn.close()
        return stats


# Convenience functions for quick integration
_brain = None

def get_brain():
    """Get singleton Brain instance"""
    global _brain
    if _brain is None:
        _brain = BrainConnector()
    return _brain

def log(agent_name: str, action: str, details: str = None, status: str = "success"):
    """Quick log function"""
    return get_brain().log_activity(agent_name, action, details, status)

def learn(agent_name: str, topic: str, content: str, source: str = "ollama"):
    """Quick learning log"""
    return get_brain().log_learning(agent_name, topic, content, source)

def start_session(agent_name: str):
    """Quick session start"""
    return get_brain().start_session(agent_name)

def end_session(session_id: int, agent_name: str):
    """Quick session end"""
    return get_brain().end_session(session_id, agent_name)


# Decorator for automatic logging
def brain_tracked(agent_name: str):
    """Decorator to automatically log function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            brain = get_brain()
            brain.log_activity(agent_name, f"called_{func.__name__}", str(kwargs)[:200] if kwargs else None)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                brain.log_activity(agent_name, f"error_{func.__name__}", str(e)[:200], "error")
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test the connector
    brain = BrainConnector()
    
    print("\n📊 Memory Brain Stats:")
    stats = brain.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test logging
    brain.log_activity("BrainConnector", "self_test", "Testing brain connector")
    print("\n✅ Test log written")
    
    # Show recent activity
    print("\n📋 Recent Activity:")
    for activity in brain.get_recent_activity(limit=5):
        print(f"   [{activity[3]}] {activity[0]}: {activity[1]}")
