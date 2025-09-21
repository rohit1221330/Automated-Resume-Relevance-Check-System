import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "resume_evaluations.db"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT NOT NULL,
            jd_filename TEXT NOT NULL,
            final_score INTEGER,
            verdict TEXT,
            strengths TEXT,
            weaknesses TEXT,
            suggestions TEXT,
            missing_skills TEXT,
            timestamp DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def save_result(resume_filename, jd_filename, result_data):
    """Saves a single evaluation result to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Extract data from the result dictionary
    feedback = result_data['semantic_match_feedback']
    missing_skills_str = ", ".join(result_data.get('missing_skills', []))
    
    cursor.execute('''
        INSERT INTO evaluations (resume_filename, jd_filename, final_score, verdict, 
                                 strengths, weaknesses, suggestions, missing_skills, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_filename,
        jd_filename,
        result_data.get('final_score'),
        result_data.get('verdict'),
        feedback.get('strengths'),
        feedback.get('weaknesses'),
        feedback.get('suggestions'),
        missing_skills_str,
        datetime.now()
    ))
    
    conn.commit()
    conn.close()

def fetch_all_results():
    """Fetches all evaluation results from the database."""
    conn = sqlite3.connect(DB_NAME)
    # Use pandas to read the SQL query into a DataFrame
    df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def delete_result(evaluation_id):
    """Deletes a specific evaluation result from the database by its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM evaluations WHERE id = ?', (evaluation_id,))
    
    conn.commit()
    conn.close()