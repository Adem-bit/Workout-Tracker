from datetime import date, timedelta
from db import get_connection

EXERCISE_LIST = [
    "pull ups",
    "chin ups",
    "dips",
    "push ups",
    "decline push ups",
    "diamond push ups",
    "wide push ups",
    "pike push ups",
    "handstand push ups",
    "australian pull ups",
    "muscle ups",
    "squats",
    "lunges",
    "pistol squats",
    "calf raises",
    "plank",
    "hanging leg raises",
    "l-sit",
    "hollow body hold",
    "arch body hold",
    "burpees",
    "mountain climbers",
    "bench press",
    "deadlift",
    "overhead press",
    "bicep curls",
    "tricep extensions",
    "lateral raises",
    "rows",
    "lat pulldowns",
]


def validate_workout_form(form):
    exercise = form.get("exercise", "").strip()
    sets_str = form.get("sets", "").strip()
    reps_str = form.get("reps", "").strip()
    weight_str = form.get("weight", "").strip()
    notes = form.get("notes", "").strip()

    errors = []
    if not exercise:
        errors.append("Exercise name is required")
    if not sets_str:
        errors.append("Number of Sets is required")
    if not reps_str:
        errors.append("Number of Reps is required")
    if not weight_str:
        errors.append("Weight is required")

    if sets_str:
        try:
            sets = int(sets_str)
        except ValueError:
            errors.append("Sets must be a number")

    if reps_str and not errors:
        try:
            reps = list(map(int, reps_str.split(",")))
        except ValueError:
            errors.append(
                "Reps must be numbers separated by commas (e.g. 10,8,6)")

    if weight_str.lower() == "bw":
        weight = "bodyweight"
    else:
        try:
            weight = float(weight_str)
        except ValueError:
            weight = weight_str

    if errors:
        return None, errors

    return {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight": weight,
        "notes": notes
    }, None


def add_workout(exercise, sets, reps, weight, notes=""):
    today = date.today().isoformat()
    reps_string = ",".join(map(str, reps))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO workouts (date, exercise, sets, reps, weight, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (today, exercise.lower().strip(), sets, reps_string, str(weight), notes))

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
    conn.close()


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
    """, (today, exercise.lower().strip(), sets, reps_string, str(weight), notes, workout_id))

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


def get_pr_history(exercise_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, reps FROM workouts WHERE exercise = ? ORDER BY date ASC", (exercise_name,))
    rows = cursor.fetchall()
    conn.close()

    labels = []
    data = []

    for date_str, reps_string in rows:
        try:
            nums = list(map(int, reps_string.split(',')))
            best = max(nums)
            labels.append(date_str)
            data.append(best)
        except (ValueError, TypeError):
            continue

    return {"labels": labels, "data": data}


def get_distinct_exercises():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT exercise FROM workouts ORDER BY exercise ASC")
    rows = cursor.fetchall()
    conn.close()

    exercises = []
    for row in rows:
        exercises.append(row[0])

    return exercises


def get_workouts_by_exercise(exercise_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM workouts WHERE exercise = ? ORDER BY date ASC", (exercise_name,))
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


def get_stats():
    workouts = get_all_workouts()

    if not workouts:
        return None

    total_workouts = len(workouts)

    today = date.today()
    week_ago = today - timedelta(days=7)
    this_week = 0

    for w in workouts:
        workout_date = date.fromisoformat(w['date'])
        if workout_date >= week_ago:
            this_week += 1

    exercise_counts = {}
    for w in workouts:
        ex = w['exercise']
        if ex in exercise_counts:
            exercise_counts[ex] += 1
        else:
            exercise_counts[ex] = 1

    favorite = max(exercise_counts, key=exercise_counts.get)

    streak = 0
    check_date = date.today()

    while True:
        date_str = check_date.isoformat()
        found = False
        for w in workouts:
            if w['date'] == date_str:
                found = True
                break

        if found:
            streak += 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    return {
        "total": total_workouts,
        "this_week": this_week,
        "favorite": favorite,
        "streak": streak
    }


def normalize_exercises():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, exercise FROM workouts")
    rows = cursor.fetchall()

    for workout_id, exercise in rows:
        normalized = exercise.lower().strip()
        if exercise != normalized:
            cursor.execute(
                "UPDATE workouts SET exercise = ? WHERE id = ?", (normalized, workout_id))

    conn.commit()
    conn.close()
