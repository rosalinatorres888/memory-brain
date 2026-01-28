#!/usr/bin/env python3
"""
Career Intelligence Assistant - Memory Brain Query Tool
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / "Documents" / "memory-brain" / "central_memory.db"

def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    try:
        conn = get_connection()
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def format_results(results, title):
    if not results:
        return f"\n### {title}\nNo results found.\n"
    output = f"\n### {title}\n"
    for i, row in enumerate(results, 1):
        output += f"\n**{i}.** "
        output += " | ".join(f"{k}: {v}" for k, v in row.items() if v is not None)
        output += "\n"
    return output

def daily_focus():
    output = "# Daily Focus Plan\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    tasks = execute_query("SELECT * FROM tasks WHERE status IN ('pending', 'in_progress') ORDER BY priority, created_at")
    output += format_results(tasks, "Prioritized Tasks")
    followups = execute_query("SELECT * FROM job_applications WHERE status IN ('applied', 'interviewing')")
    output += format_results(followups, "Applications Needing Follow-up")
    return output

def career_report():
    output = "# Career Intelligence Report\n"
    output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    pipeline = execute_query("SELECT status, COUNT(*) as count FROM job_applications GROUP BY status")
    output += format_results(pipeline, "Application Pipeline")
    tasks = execute_query("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10")
    output += format_results(tasks, "Recent Tasks")
    return output

def apply_to_company(company):
    output = f"# Application Intelligence: {company}\n"
    apps = execute_query("SELECT * FROM job_applications WHERE company LIKE ?", (f'%{company}%',))
    output += format_results(apps, f"Applications to {company}")
    connections = execute_query("SELECT * FROM linkedin_insights WHERE content LIKE ?", (f'%{company}%',))
    output += format_results(connections, f"Connections at {company}")
    return output

def linkedin_strategy():
    output = "# LinkedIn Strategy\n"
    insights = execute_query("SELECT * FROM linkedin_insights ORDER BY generated_at DESC LIMIT 10")
    output += format_results(insights, "Recent Insights")
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_memory_brain.py [daily|report|linkedin|apply <company>|custom <query>]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    if cmd == "daily":
        print(daily_focus())
    elif cmd == "report":
        print(career_report())
    elif cmd == "linkedin":
        print(linkedin_strategy())
    elif cmd == "apply" and len(sys.argv) >= 3:
        print(apply_to_company(" ".join(sys.argv[2:])))
    elif cmd == "custom" and len(sys.argv) >= 3:
        print(format_results(execute_query(sys.argv[2]), "Custom Query"))
    else:
        print("Unknown command")
