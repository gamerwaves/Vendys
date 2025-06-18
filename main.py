import math
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from threading import Thread

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file!")

app = Flask(__name__)


def run():
    app.run(host="0.0.0.0", port=5000)


def keep_alive():
    t = Thread(target=run)
    t.start()


def calculate_points(dollars, premium=False):
    if dollars < 1:
        return 0

    base_rate = 5 if not premium else 3
    bonus = math.log2(dollars) * (2 if not premium else 1)
    total_points = base_rate * dollars + bonus
    return round(total_points)


def add_points_to_user(rfid_id, normal_points, premium_points):
    client = MongoClient(MONGO_URI)
    db = client["ids"]
    cards = db["cards"]

    result = cards.update_one({"rfid_id": rfid_id}, {
        "$inc": {
            "normal_points": normal_points,
            "premium_points": premium_points
        }
    })

    if result.matched_count == 0:
        new_user = {
            "rfid_id": rfid_id,
            "normal_points": normal_points,
            "premium_points": premium_points
        }
        cards.insert_one(new_user)
        client.close()
        return f"User '{rfid_id}' not found, created new user with points."
    else:
        client.close()
        return f"Updated points for user '{rfid_id}': " \
               f"{'added' if normal_points >= 0 else 'subtracted'} {abs(normal_points)} normal points, " \
               f"{'added' if premium_points >= 0 else 'subtracted'} {abs(premium_points)} premium points."


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/add_points", methods=["POST"])
def add_points():
    operation = request.form.get("operation", "add")
    user_type = request.form.get("user_type")
    dollar_amount = request.form.get("dollar_amount")
    rfid_id = request.form.get("rfid_id")

    if user_type not in ['p', 'n']:
        return "Invalid user type. Use 'p' for premium or 'n' for normal.", 400
    if operation not in ['add', 'subtract']:
        return "Invalid operation. Use 'add' or 'subtract'.", 400

    try:
        dollars = float(dollar_amount)
        if dollars < 1:
            return "Dollar amount must be 1 or greater.", 400
    except (ValueError, TypeError):
        return "Invalid dollar amount.", 400

    if not rfid_id:
        return "RFID card ID is required.", 400

    if user_type == 'p':
        normal_points = 0
        premium_points = calculate_points(dollars, premium=True)
    else:
        normal_points = calculate_points(dollars, premium=False)
        premium_points = 0

    if operation == 'subtract':
        normal_points = -normal_points
        premium_points = -premium_points

    message = add_points_to_user(rfid_id, normal_points, premium_points)
    return render_template("result.html", message=message)


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        dollars = float(data.get("dollars", 0))
        premium = bool(data.get("premium", False))
        points = calculate_points(dollars, premium)
        return jsonify({"points": points}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    keep_alive()
