from flask import jsonify

from app.app import app


@app.route("/stats")
def stats():
    return jsonify(app.stats), 200
