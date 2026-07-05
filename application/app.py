"""
TIER 2: APPLICATION LAYER — API / ROUTES
============================================================
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

import logic
import data_access

app = Flask(__name__)
CORS(app)  # presentation tier may run on a different origin locally


@app.route("/health")
def health():
    try:
        data_access.get_connection().close()
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route("/api/polls", methods=["GET"])
def get_polls():
    polls = data_access.list_polls()
    output = []
    for poll in polls:
        evaluation = logic.compute_results(poll["_options"])
        output.append({
            "id": poll["id"],
            "question": poll["question"],
            "created_at": poll["created_at"].isoformat() if poll["created_at"] else None,
            **evaluation,
        })
    return jsonify(output), 200


@app.route("/api/polls/<int:poll_id>", methods=["GET"])
def get_poll(poll_id):
    poll = data_access.get_poll(poll_id)
    if not poll:
        return jsonify({"error": "poll not found"}), 404
    evaluation = logic.compute_results(poll["_options"])
    return jsonify({
        "id": poll["id"], "question": poll["question"],
        "created_at": poll["created_at"].isoformat() if poll["created_at"] else None,
        **evaluation,
    }), 200


@app.route("/api/polls", methods=["POST"])
def create_poll():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    options = data.get("options") or []

    error = logic.validate_poll_input(question, options)
    if error:
        return jsonify({"error": error}), 400

    poll_id = data_access.create_poll(question, options)
    return jsonify(data_access.get_poll(poll_id)), 201


@app.route("/api/polls/<int:poll_id>/vote", methods=["POST"])
def vote(poll_id):
    data = request.get_json(silent=True) or {}
    option_id = data.get("option_id")
    if not option_id:
        return jsonify({"error": "'option_id' is required"}), 400

    updated = data_access.cast_vote(poll_id, option_id)
    if updated == 0:
        return jsonify({"error": "poll or option not found"}), 404

    poll = data_access.get_poll(poll_id)
    evaluation = logic.compute_results(poll["_options"])
    return jsonify({
        "id": poll["id"], "question": poll["question"], **evaluation,
    }), 200


@app.route("/api/polls/<int:poll_id>", methods=["DELETE"])
def remove_poll(poll_id):
    deleted = data_access.delete_poll(poll_id)
    if deleted == 0:
        return jsonify({"error": "poll not found"}), 404
    return jsonify({"deleted": poll_id}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
