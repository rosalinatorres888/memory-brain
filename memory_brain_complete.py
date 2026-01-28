import sqlite3
from datetime import datetime
from pathlib import Path
import uuid

class MemoryBrain:
    def __init__(self):
        self.db_path = Path("/Users/rosalinatorres/Documents/memory-brain/central_memory.db")
        self._init_database()
        print(f"✓ Memory Brain online at: {self.db_path}")
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, title TEXT, priority TEXT, status TEXT, agent_source TEXT, created_at TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_applications (id TEXT PRIMARY KEY, company TEXT, role TEXT, status TEXT, match_score REAL, created_at TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS linkedin_insights (id TEXT PRIMARY KEY, insight_type TEXT, content TEXT, confidence REAL, generated_at TEXT)")
        conn.commit()
        conn.close()

    def add_job(self, company: str, role: str, match_score: float = 0):
        job_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO job_applications VALUES (?, ?, ?, 'researching', ?, ?)",
                      (job_id, company, role, match_score, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"✓ Tracking Role: {role}")

    def remember_linkedin_insight(self, insight_type: str, content: str, confidence: float = 1.0):
        insight_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO linkedin_insights VALUES (?, ?, ?, ?, ?)",
                      (insight_id, insight_type, content, confidence, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"✓ Insight Saved: {insight_type}")

    def show_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM job_applications")
        jobs = cursor.fetchall()
        cursor.execute("SELECT insight_type FROM linkedin_insights")
        insights = cursor.fetchall()
        print(f"\n🧠 BRAIN STATUS: {len(jobs)} Roles | {len(insights)} Insights")
        for j in jobs[-4:]: print(f"  • Role: {j[0]}")
        conn.close()
