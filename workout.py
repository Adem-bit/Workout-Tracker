from datetime import date
from db import get_connection


def add_workout(exercise, sets, reps, weight):
    today = date.today().isoformat()
    reps_string = ",".join(map(str, reps))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO workouts (date, exercise, sets, reps, weight)
    VALUES (?, ?, ?, ?, ?)
    """, (today, exercise, sets, reps_string, str(weight)))

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
            "weight": row[5]
        }
        workouts_list.append(workout_dict)

    return workouts_list


def delete_workout(workout_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))

    conn.commit()
    conn.cursor()
