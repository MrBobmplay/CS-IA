from flask import Flask, jsonify, render_template, request, session

import database
from forecast_manager import forecast_manager
from heat_manager import MAX_SURFERS, heat_manager
from score_manager import score_manager

app = Flask(__name__)
app.secret_key = "escola-de-surf-peniche"


def is_director():
    return session.get("role") == "director"


def not_allowed():
    return jsonify({"error": "Only the director can do that."}), 403


def bad_input(error):
    return jsonify({"error": str(error)}), 400


def heats_as_list(heats):
    heat_list = []
    for heat in heats:
        heat_list.append(heat.as_dict())
    return heat_list


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/session")
def get_session():
    return jsonify({"role": session.get("role", "viewer"),
                    "username": session.get("username", "")})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    rows = database.query(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (data.get("username", ""), database.hash_password(data.get("password", ""))))

    if len(rows) == 0:
        return jsonify({"error": "Wrong username or password."}), 401

    session["username"] = rows[0]["username"]
    session["role"] = rows[0]["role"]
    return jsonify({"role": rows[0]["role"], "username": rows[0]["username"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"role": "viewer"})


@app.route("/api/surfers")
def get_surfers():
    surfers = []
    for surfer in heat_manager.get_surfers():
        surfers.append(surfer.as_dict())
    return jsonify({"surfers": surfers, "max_surfers": MAX_SURFERS})


@app.route("/api/surfers", methods=["POST"])
def add_surfer():
    if not is_director():
        return not_allowed()

    data = request.get_json()
    try:
        heat_manager.add_surfer(data.get("name", ""),
                                int(data.get("skill", 0)),
                                data.get("group_name", ""))
    except (ValueError, TypeError) as error:
        return bad_input(error)
    return get_surfers()


@app.route("/api/heats")
def get_heats():
    round_number = int(request.args.get("round", 1))
    return jsonify({"round_number": round_number,
                    "rounds": heat_manager.rounds(),
                    "heats": heats_as_list(heat_manager.get_heats(round_number))})


@app.route("/api/draw", methods=["POST"])
def draw():
    if not is_director():
        return not_allowed()

    try:
        heat_manager.draw_round(1)
    except ValueError as error:
        return bad_input(error)
    return get_heats()


@app.route("/api/heats/<int:heat_id>")
def get_heat(heat_id):
    results = score_manager.heat_results(heat_id)
    if results is None:
        return jsonify({"error": "That heat does not exist."}), 404
    return jsonify(results)


@app.route("/api/scores", methods=["POST"])
def add_score():
    if not is_director():
        return not_allowed()

    data = request.get_json()
    try:
        heat_id = int(data.get("heat_id"))
        score_manager.add_score(heat_id,
                                int(data.get("surfer_id")),
                                float(data.get("raw_score")),
                                float(data.get("weight", 1.0)))
    except (ValueError, TypeError) as error:
        return bad_input(error)

    return jsonify(score_manager.heat_results(heat_id))


@app.route("/api/advance", methods=["POST"])
def advance():
    if not is_director():
        return not_allowed()

    data = request.get_json()
    try:
        round_number = int(data.get("round_number", 1))
        new_heats = score_manager.advance(round_number, int(data.get("top_n", 2)))
    except (ValueError, TypeError) as error:
        return bad_input(error)

    return jsonify({"round_number": round_number + 1,
                    "rounds": heat_manager.rounds(),
                    "heats": heats_as_list(new_heats)})


@app.route("/api/leaderboard")
def leaderboard():
    return jsonify({"leaderboard": score_manager.leaderboard(),
                    "role": session.get("role", "viewer")})


@app.route("/api/forecast")
def get_forecast():
    return jsonify({"slots": forecast_manager.ranked_slots()})


@app.route("/api/forecast", methods=["POST"])
def add_forecast():
    if not is_director():
        return not_allowed()

    data = request.get_json()
    try:
        forecast_manager.add_slot(data.get("slot_time", ""),
                                  float(data.get("wave_height")),
                                  float(data.get("tide_level")))
    except (ValueError, TypeError) as error:
        return bad_input(error)
    return get_forecast()


@app.route("/api/sheet")
def sheet():
    round_number = int(request.args.get("round", 1))
    return jsonify({"round_number": round_number,
                    "heats": heats_as_list(heat_manager.get_heats(round_number))})


if __name__ == "__main__":
    database.setup()
    app.run(debug=True, port=5000)
