import requests
from flask import Flask, request, jsonify
from datetime import date, datetime, timedelta

app = Flask(__name__)

daily_totals: dict[str, float] = {}
user_goals: dict[str, float] = {}

REMINDER_SERVICE_URL = "http://localhost:5000"
WATER_SERVICE_PORT = 5001
DEFAULT_GOAL_ML = 2000.0

def get_goal(user_id: str) -> float:
    return user_goals.get(user_id, DEFAULT_GOAL_ML)

def schedule_water_reminder(user_id: str, message: str, minutes_from_now: int = 60, priority: str = "medium"):
    due = (datetime.now() + timedelta(minutes=minutes_from_now)).isoformat()
    try:
        res = requests.post(f"{REMINDER_SERVICE_URL}/reminders", json={
         "user_id": user_id,
        "reminder_message": message,
        "due_date_time": due,
        "priority": priority,
        "notification_method": "push"   
        }, timeout=3)
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.put("/goal")
def set_goal():
    body = request.get_json() or {}
    user_id = body.get("user_id")
    goal_ml = body.get("goal_ml")

    if not user_id:
        return jsonify({"error": "missing user id"}), 400
    if goal_ml is None:
        return jsonify({"error": "missing goal_ml"}), 400
    try:
        goal_ml = float(goal_ml)
    except (TypeError, ValueError):
        return jsonify({"error": "goal_ml must be a number"}), 400
    if goal_ml <= 0:
        return jsonify({"error": "goal_ml must be positive"}), 400
    
    user_goals[user_id] = goal_ml

    schedule_water_reminder(
        user_id,
        f"Your daily water goal is set to {round(goal_ml)} ml. Stay hydrated",
        minutes_from_now=1,
        priority="low"
    )

    return jsonify({
        "user_id": user_id,
        "goal_ml": goal_ml,
        "message": f"Daily goal updated to {round(goal_ml)} ml."
    })

@app.post("/intake")
def add_intake():
    body = request.get_json() or {}
    amount = body.get("amount_ml")
    user_id = body.get("user_id", "default_user")

    if amount is None:
        return jsonify({"error": "Missing amount"}), 400
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be a number"}), 400
    if amount <= 0:
        return jsonify({"error": "amount_ml must be positive"}), 400
    
    key = f"{user_id}:{date.today()}"
    daily_totals[key] = daily_totals.get(key, 0.0) + amount
    total = daily_totals[key]
    goal = get_goal(user_id)
    reminder_info = None

    if total >= goal:
        reminder_info = schedule_water_reminder(
            user_id, f"Goal reached! You've hit {round(total)} ml today",
            minutes_from_now=1, priority="low"
        )

    return jsonify({
        "date": key,
        "added_ml": round(amount, 2),
        "total_ml": round(total, 2),
        "goal_ml": goal,
        "goal_reached": total >= goal,
        "reminder_scheduled": reminder_info,
    }), 201

@app.get("/goal/<user_id>")
def get_user_goal(user_id):
    return jsonify({
        "user_id": user_id,
        "goal_ml": get_goal(user_id)
    })

@app.get("/intake/today")
def get_today():
    user_id = request.args.get("user_id", "default_user")
    key = f"{user_id}:{date.today()}"
    total = daily_totals.get(key, 0.0)
    goal = get_goal(user_id)
    return jsonify({
        "date": key,
        "total_ml": round(total, 2),
        "goal_ml": goal,
        "remaining_ml": round(max(goal - total, 0), 2),
        "goal_reached": total >= goal
    })

if __name__ == "__main__":
    app.run(port=WATER_SERVICE_PORT)
