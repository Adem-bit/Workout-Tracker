import sqlite3

DB_NAME = "workouts.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    print("INIT DB RUNNING")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        exercise TEXT,
        sets INTEGER,
        reps TEXT,
        weight TEXT
    )
    """)

    conn.commit()
    conn.close()
