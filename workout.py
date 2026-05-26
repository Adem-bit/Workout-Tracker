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


def validate_api_workout(data):
    errors = []

    exercise = data.get("exercise", "").strip().lower()
    sets = data.get("sets", 0)
    reps = data.get("reps", [])
    weight = data.get("weight", "")
    notes = data.get("notes" "")

    if not exercise:
        errors.append("Exercise name is required")
    if not isinstance(sets, int) or sets <= 0:
        errors.append("Sets must be a positive number")
    if not isinstance(reps, list) or len(reps) == 0:
        errors.append("Reps must be a list of numbers")
    if not weight:
        errors.append("Weight is required")

    if errors:
        return None, errors

    if str(weight).lower() == 'bw':
        weight = "bodyweight"
    else:
        try:
            weight = float(weight)
        except ValueError:
            weight = str(weight)

        return {
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "notes": notes
        }, None


def validate_workout_form(form):
    exercise = form.get("exercise", "") if hasattr(form, 'get') else form.get(
        "exercise", "").strip() if isinstance(form.get("exercise", ""), str) else ""

    if isinstance(form, dict) and not hasattr(form, 'get'):
        exercise = form.get("exercise", "").strip() if isinstance(
            form.get("exercise"), str) else ""
        sets_str = str(form.get("sets", ""))
        reps_str = str(form.get("reps", ""))
        weight_str = str(form.get("weight", ""))
        notes = str(form.get("notes", ""))
    else:
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
            reps = list(map(int, reps_str.split(',')))
        except ValueError:
            errors.append(
                "Reps must be numbers seperated by commas (e.g. 10,8,6)")

    if weight_str.lower() == 'bw':
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
    INSERT INTO workouts (date, exercise, weight, notes)
    VALUES (?, ?, ?, ?)
""", (today, exercise, str(weight), notes))

    workout_id = cursor.lastrowid

    for i, rep in enumerate(reps, start=1):
        cursor.execute("""
    INSERT INTO sets (workout_id, set_number, reps)
    VALUES (?, ?, ?)
""", (workout_id, i, rep))

    conn.commit()
    conn.close()


def get_all_workouts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workouts ORDER BY date ASC")
    workout_rows = cursor.fetchall()

    workouts_list = []
    for row in workout_rows:
        workout_id = row[0]
        cursor.execute(
            "SELECT set_number, reps FROM sets WHERE workout_id = ? ORDER BY set_number ASC", (workout_id,))
        sets_rows = cursor.fetchall()

        reps_list = [str(s[1]) for s in sets_rows]
        total_sets = len(sets_rows)

        workout_dict = {
            "id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": total_sets,
            "reps": ",".join(reps_list),
            "weight": row[3],
            "notes": row[4] if len(row) > 4 else ""
        }
        workouts_list.append(workout_dict)

    conn.close()
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

    cursor.execute("""
    SELECT w.exercise, s.reps
    FROM workouts w
    JOIN sets s ON w.id = s.workout_id
""")

    rows = cursor.fetchall()
    conn.close()

    prs = {}
    for exercise, rep in rows:
        if rep > prs.get(exercise, 0):
            prs[exercise] = rep

    return prs


def update_workout(workout_id, exercise, sets, reps, weight, notes=""):
    today = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE workouts
    SET date = ?, exercise = ?, weight = ?, notes = ?
    WHERE id = ?
    """, (today, exercise.lower().strip(), str(weight), notes, workout_id))

    cursor.execute("DELETE FROM sets WHERE workout_id = ?", (workout_id))

    for i, rep in enumerate(reps, start=1):
        cursor.execute("""
            INSERT INTO sets (workout_id, set_number, reps)
            VALUES (?, ?, ?)
""", (workout_id, i, rep))

    conn.commit()
    conn.close()


def get_workout(workout_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    cursor.execute(
        "SELECT set_number, reps FROM sets WHERE workout_id = ? ORDER BY set_number ASC," (workout_id,))
    sets_rows = cursor.fetchall()
    conn.close()

    reps_list = [str(s[1]) for s in sets_rows]
    total_sets = len(sets_rows)

    if row:
        return {
            "id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": total_sets,
            "reps": ",".join(reps_list),
            "weight": row[3],
            "notes": row[4] if len(row) > 4 else ""
        }
    return None


def get_pr_history(exercise_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT w.date, s.reps
        FROM workouts w
        JOIN sets s ON w.id = s.workout_id
        WHERE w.exercise = ?
        ORDER by w.date ASC
""", (exercise_name,))
    rows = cursor.fetchall()
    conn.close()

    labels = []
    data = []

    for date_str, rep in rows:
        labels.append(date_str)
        data.append(rep)

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
    workout_rows = cursor.fetchall()

    workouts_list = []
    for row in workout_rows:
        workout_id = row[0]
        cursor.execute(
            "SELECT set_number, reps FROM sets WHERE workout_id = ? ORDER BY set_number ASC", (workout_id,))
        sets_rows = cursor.fetchall()

        reps_list = [str(s[1]) for s in sets_rows]
        total_sets = len(sets_rows)
        workout_dict = {
            "id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": total_sets,
            "reps": ",".join(reps_list),
            "weight": row[3],
            "notes": row[4] if len(row) > 4 else ""
        }
        workouts_list.append(workout_dict)

    conn.close()
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


def migrate_to_sets_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, reps FROM workouts")
    old_workouts = cursor.fetchall()

    for workout_id, reps_string in old_workouts:
        try:
            reps_list = reps_string.split(',')
            for i, rep in enumerate(reps_list, start=1):
                cursor.execute(
                    "INSERT INTO sets (workout_id, set_number, reps) VALUES (?, ?, ?)",
                    (workout_id, i, int(rep.strip()))
                )
        except:
            continue

        conn.commit()
        conn.close()
        print("Migration complete.")
