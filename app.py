from flask import Flask, render_template, request, redirect, Response, jsonify
from workout import add_workout, get_all_workouts, delete_workout, get_personal_records, get_workout, update_workout, get_pr_history, get_workouts_by_exercise, get_distinct_exercises, get_stats, EXERCISE_LIST, validate_api_workout, validate_workout_form
from db import init_db
from datetime import datetime

app = Flask(__name__)


def format_date(value):
    date_obj = datetime.strptime(value, "%Y-%m-%d")
    return date_obj.strftime("%A, %B %d %Y")


app.jinja_env.filters['format_date'] = format_date

init_db()


@app.route("/")
def home():
    filter_exercise = request.args.get("exercise", "")

    if filter_exercise:
        all_workouts = get_workouts_by_exercise(filter_exercise)
    else:
        all_workouts = get_all_workouts()

    exercises = get_distinct_exercises()
    stats = get_stats()

    return render_template("index.html", workouts=all_workouts, exercises=exercises, current_filter=filter_exercise, active_page="home", stats=stats)


# all API routes

@app.route("/api/workouts", methods=["GET"])
def api_get_workouts():
    workouts = get_all_workouts()
    return jsonify(workouts)


@app.route("/api/workouts", methods=["POST"])
def api_add_workout():
    data = request.get_json()
    result, errors = validate_api_workout(data)
    if errors:
        return jsonify({"errors": errors}), 400
    add_workout(result["exercise"], result["sets"],
                result["reps"], result["weight"], result["notes"])
    return jsonify({"message": "Workout added"}), 201


@app.route("/api/workouts/<int:id>", methods=["GET"])
def api_get_workout(id):
    workout = get_workout(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout)


@app.route("/api/workouts/<int:id>", methods=["PUT"])
def api_update_workout(id):
    workout = get_workout(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    data = request.get_json()
    result, errors = validate_api_workout(data)
    if errors:
        return jsonify({"errors": errors}), 400
    update_workout(id, result["exercise"], result["sets"],
                   result["reps"], result["weight"], result["notes"])
    return jsonify({"message": "Workout updated"})


@app.route("/api/workouts/<int:id>", methods=["DELETE"])
def api_delete_workout(id):
    workout = get_workout(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    delete_workout(id)
    return jsonify({"message": "Workout deleted"})


@app.route("/api/prs", methods=["GET"])
def api_get_prs():
    prs = get_personal_records()
    return jsonify(prs)


@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    stats = get_stats()
    return jsonify(stats)


@app.route("/api/exercises", methods=["GET"])
def api_get_exercises():
    return jsonify(EXERCISE_LIST)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data, errors = validate_workout_form(request.form)
        if errors:
            return render_template("add.html", errors=errors, active_page="add", exercise_list=EXERCISE_LIST)

        add_workout(data["exercise"], data["sets"],
                    data["reps"], data["weight"], data["notes"])

        return redirect("/")

    return render_template("add.html", active_page='add', exercise_list=EXERCISE_LIST)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_workout(id)
    return redirect("/")


@app.route("/prs")
def personal_records():
    prs = get_personal_records()
    return render_template("prs.html", prs=prs, active_page="prs")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    workout = get_workout(id)
    if not workout:
        return redirect("/")

    if request.method == "POST":
        data, errors = validate_workout_form(request.form)
        if errors:
            return render_template("edit.html", workout=workout, errors=errors, active_page="edit", exercise_list=EXERCISE_LIST)

        update_workout(id, data["exercise"], data["sets"],
                       data["reps"], data["weight"], data["notes"])
        return redirect("/")

    return render_template("edit.html", workout=workout, active_page="edit", exercise_list=EXERCISE_LIST)


@app.route("/export")
def export_csv():
    workouts = get_all_workouts()

    csv_data = "Date,Exercise,Sets,Reps,Weight,Notes\n"

    for w in workouts:
        csv_data += f'"{w['date']}","{w['exercise']}",{w['sets']},"{w['reps']}","{w['weight']}","{w['notes']}"\n'

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=workouts.csv"}
    )


@app.route("/api/pr-history/<exercise>")
def pr_history(exercise):
    return jsonify(get_pr_history(exercise))


if __name__ == "__main__":
    app.run(debug=True)
