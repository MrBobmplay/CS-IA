"""Surf Heat Manager: the web server that joins the browser to the database."""

from flask import Flask, jsonify, render_template, request, session

import database
from forecast_manager import forecast_manager
from heat_manager import MAX_SURFERS, heat_manager
from score_manager import score_manager

app = Flask(__name__)
app.secret_key = "escola-de-surf-peniche"


def is_director():
    """Only a logged in director may change data; everyone else can look."""
    return session.get("role") == "director"


def director_only():
    """Return an error response if the current user may not write."""
    if not is_director():
        return jsonify({"error": "Only the director can do that."}), 403
    return None


# ---- Pages --------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---- Login (SC16) -------------------------------------------------------

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
    if not rows:
        return jsonify({"error": "Wrong username or password."}), 401

    session["username"] = rows[0]["username"]
    session["role"] = rows[0]["role"]
    return jsonify({"role": rows[0]["role"], "username": rows[0]["username"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"role": "viewer"})


# ---- Surfers (SC1, SC2) -------------------------------------------------

@app.route("/api/surfers")
def get_surfers():
    return jsonify({"surfers": [s.as_dict() for s in heat_manager.get_surfers()],
                    "max_surfers": MAX_SURFERS})


@app.route("/api/surfers", methods=["POST"])
def add_surfer():
    blocked = director_only()
    if blocked:
        return blocked

    data = request.get_json()
    try:
        heat_manager.add_surfer(data.get("name", ""),
                                int(data.get("skill", 0)),
                                data.get("group_name", ""))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    return get_surfers()


# ---- Heats (SC3, SC4, SC5) ---------------------------------------------

@app.route("/api/heats")
def get_heats():
    round_number = int(request.args.get("round", 1))
    return jsonify({"round_number": round_number,
                    "rounds": heat_manager.rounds(),
                    "heats": [h.as_dict() for h in heat_manager.get_heats(round_number)]})


@app.route("/api/draw", methods=["POST"])
def draw():
    blocked = director_only()
    if blocked:
        return blocked
    try:
        heat_manager.draw_round(1)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return get_heats()


# ---- Scores (SC6, SC7, SC8) --------------------------------------------

@app.route("/api/heats/<int:heat_id>")
def get_heat(heat_id):
    results = score_manager.heat_results(heat_id)
    if results is None:
        return jsonify({"error": "That heat does not exist."}), 404
    return jsonify(results)


@app.route("/api/scores", methods=["POST"])
def add_score():
    blocked = director_only()
    if blocked:
        return blocked

    data = request.get_json()
    try:
        heat_id = int(data.get("heat_id"))
        score_manager.add_score(heat_id,
                                int(data.get("surfer_id")),
                                float(data.get("raw_score")),
                                float(data.get("weight", 1.0)))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(score_manager.heat_results(heat_id))


# ---- Progression (SC9, SC10) -------------------------------------------

@app.route("/api/advance", methods=["POST"])
def advance():
    blocked = director_only()
    if blocked:
        return blocked

    data = request.get_json()
    try:
        heats = score_manager.advance(int(data.get("round_number", 1)),
                                      int(data.get("top_n", 2)))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"round_number": heats[0].round_number if heats else None,
                    "rounds": heat_manager.rounds(),
                    "heats": [h.as_dict() for h in heats]})


# ---- Leaderboard (SC11, SC12) ------------------------------------------

@app.route("/api/leaderboard")
def leaderboard():
    return jsonify({"leaderboard": score_manager.leaderboard(),
                    "role": session.get("role", "viewer")})


# ---- Forecast (SC13) ----------------------------------------------------

@app.route("/api/forecast")
def get_forecast():
    return jsonify({"slots": forecast_manager.ranked_slots()})


@app.route("/api/forecast", methods=["POST"])
def add_forecast():
    blocked = director_only()
    if blocked:
        return blocked

    data = request.get_json()
    try:
        forecast_manager.add_slot(data.get("slot_time", ""),
                                  float(data.get("wave_height")),
                                  float(data.get("tide_level")))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    return get_forecast()


# ---- Printable heat sheet (SC14, SC15) ---------------------------------

@app.route("/api/sheet")
def sheet():
    round_number = int(request.args.get("round", 1))
    return jsonify({"round_number": round_number,
                    "heats": [h.as_dict() for h in heat_manager.get_heats(round_number)]})


if __name__ == "__main__":
    database.setup()
    app.run(debug=True, port=5000)
