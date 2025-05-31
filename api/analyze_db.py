import sqlite3

DB_PATH = "analysis.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS analysis (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT,
        date TEXT,
        result TEXT,
        video_filename TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_analysis(id, user_id, title, date, result, video_filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO analysis (id, user_id, title, date, result, video_filename) VALUES (?, ?, ?, ?, ?, ?)",
        (id, user_id, title, date, result, video_filename)
    )
    conn.commit()
    conn.close()

def get_analyses_for_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, date, result, video_filename FROM analysis WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "date": r[2], "result": r[3], "video_filename": r[4]}
        for r in rows
    ]

def get_analysis_detail(user_id, analysis_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, date, result, video_filename FROM analysis WHERE user_id = ? AND id = ?", (user_id, analysis_id))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "title": row[1], "date": row[2], "result": row[3], "video_filename": row[4]}
    return None

init_db()