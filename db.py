import sqlite3

DB_NAME = "workouts.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        exercise TEXT,
        weight TEXT,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        set_number INTEGER,
        reps INTEGER,
        FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE
    )  
""")

    conn.commit()
    conn.close()
