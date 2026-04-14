from flask import Flask, render_template, request, redirect
from workout import add_workout, get_all_workouts
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
    all_workouts = get_all_workouts()
    return render_template("index.html", workouts=all_workouts)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        exercise = request.form.get("exercise", "").strip()
        sets_str = request.form.get("sets", "").strip()
        reps_str = request.form.get("reps", "").strip()
        weight_str = request.form.get("weight", "").strip()

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
                    "Reps must be numbers separated by commas (e.g. 10,8,7)")

        if errors:
            return render_template("add.html", errors=errors)

        sets = int(sets_str)
        reps = list(map(int, reps_str.split(",")))

        if weight_str.lower() == "bw":
            weight = "bodyweight"
        else:
            try:
                weight = float(weight_str)
            except ValueError:
                weight = weight_str

        add_workout(exercise, sets, reps, weight)

        return redirect("/")

    return render_template("add.html")


if __name__ == "__main__":
    app.run(debug=True)
