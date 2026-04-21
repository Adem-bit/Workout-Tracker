from datetime import date
from db import get_connection


def add_workout(exercise, sets, reps, weight, notes=""):
    today = date.today().isoformat()
    reps_string = ",".join(map(str, reps))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO workouts (date, exercise, sets, reps, weight, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (today, exercise, sets, reps_string, str(weight), notes))

    conn.commit()
    conn.close()


def get_all_workouts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workouts ORDER BY date ASC")

    rows = cursor.fetchall()
    conn.close()

    workouts_list = []
    for row in rows:
        workout_dict = {
            "id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": row[3],
            "reps": row[4],
            "weight": row[5],
            "notes": row[6] if len(row) > 6 else ""
        }
        workouts_list.append(workout_dict)

    return workouts_list


def delete_workout(workout_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))

    conn.commit()
    conn.cursor()


def get_personal_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT exercise, reps FROM workouts")
    rows = cursor.fetchall()
    conn.close()

    prs = {}
    for exercise, reps_string in rows:
        try:
            nums = list(map(int, reps_string.split(",")))
            best = max(nums)
        except (ValueError, TypeError):
            continue

        if best > prs.get(exercise, 0):
            prs[exercise] = best

    return prs


def update_workout(workout_id, exercise, sets, reps, weight, notes=""):
    today = date.today().isoformat()
    reps_string = ",".join(map(str, reps))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE workouts
    SET date = ?, exercise = ?, sets = ?, reps = ?, weight = ?, notes = ?
    WHERE id = ?
    """, (today, exercise, sets, reps_string, str(weight), notes, workout_id))

    conn.commit()
    conn.close()


def get_workout(workout_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": row[3],
            "reps": row[4],
            "weight": row[5],
            "notes": row[6] if len(row) > 6 else ""
        }
    return None
