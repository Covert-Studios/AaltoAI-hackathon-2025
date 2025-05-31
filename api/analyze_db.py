import sqlite3
from fastapi import APIRouter
from pydantic import BaseModel

DB_PATH = "analysis.sqlite3"
router = APIRouter()

class DeleteAnalysisRequest(BaseModel):
    user_id: str
    analysis_id: str

class DeleteAllAnalysesRequest(BaseModel):
    user_id: str

class RenameAnalysisRequest(BaseModel):
    user_id: str
    analysis_id: str
    new_title: str

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
        video_filename TEXT,
        score INTEGER
    )
    """)
    conn.commit()
    conn.close()

def insert_analysis(id, user_id, title, date, explanation, filename, score):
    """Insert a new analysis into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO analysis (id, user_id, title, date, result, video_filename, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (id, user_id, title, date, explanation, filename, score)
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
    c.execute("SELECT id, user_id, title, date, result, video_filename, score FROM analysis WHERE user_id = ? AND id = ?", (user_id, analysis_id))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "date": row[3],
            "result": row[4],
            "video_filename": row[5],
            "score": row[6]
        }
    return None

def delete_analysis(user_id, analysis_id):
    """Delete a specific analysis for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM analysis WHERE user_id = ? AND id = ?", (user_id, analysis_id))
    conn.commit()
    conn.close()

def delete_all_analyses_for_user(user_id):
    """Delete all analyses for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM analysis WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def rename_analysis(user_id, analysis_id, new_title):
    """Rename the title of a specific analysis for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE analysis SET title = ? WHERE user_id = ? AND id = ?",
        (new_title, user_id, analysis_id)
    )
    conn.commit()
    conn.close()

@router.post("/delete_analysis")
def api_delete_analysis(req: DeleteAnalysisRequest):
    delete_analysis(req.user_id, req.analysis_id)
    return {"status": "success"}

@router.post("/delete_all_analyses")
def api_delete_all_analyses(req: DeleteAllAnalysesRequest):
    delete_all_analyses_for_user(req.user_id)
    return {"status": "success"}

@router.post("/rename_analysis")
def api_rename_analysis(req: RenameAnalysisRequest):
    rename_analysis(req.user_id, req.analysis_id, req.new_title)
    return {"status": "success"}

init_db()