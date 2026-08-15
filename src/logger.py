import sqlite3
import time
from datetime import datetime

DB_PATH = "agent_logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            product_request TEXT,
            final_description TEXT,
            final_score INTEGER,
            status TEXT,
            total_attempts INTEGER,
            duration_seconds REAL
        )
    """)
    conn.commit()
    conn.close()

def log_run(product_request, description, score, status, total_attempts, duration_seconds):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO runs (timestamp, product_request, final_description, final_score, status, total_attempts, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        product_request,
        description,
        score,
        status,
        total_attempts,
        duration_seconds
    ))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(final_score), SUM(total_attempts), AVG(duration_seconds) FROM runs")
    total_runs, avg_score, total_attempts, avg_duration = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM runs WHERE status = 'APPROVED'")
    approved = cursor.fetchone()[0]
    conn.close()
    return {
        "total_runs": total_runs,
        "avg_score": round(avg_score, 2) if avg_score else 0,
        "approval_rate": round((approved / total_runs) * 100, 1) if total_runs else 0,
        "avg_attempts_per_run": round(total_attempts / total_runs, 2) if total_runs else 0,
        "avg_duration_seconds": round(avg_duration, 2) if avg_duration else 0
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    print(get_stats())