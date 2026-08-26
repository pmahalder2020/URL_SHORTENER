from flask import Flask, request, jsonify, redirect

import base62
import db
from rate_limiter import is_allowed

app = Flask(__name__)
db.init_db()


@app.route("/")
def home():
    return {"message": "URL Shortener API is running"}


@app.route("/shorten", methods=["POST"])
def shorten():
    # Rate limit: 5 requests per minute per IP
    client_ip = request.remote_addr
    if not is_allowed(client_ip, max_requests=5, window_seconds=60):
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    data = request.get_json(silent=True) or {}
    long_url = data.get("url")

    if not long_url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    # Very basic validation — real-world version would use a proper URL parser
    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    new_id = db.insert_url(long_url)
    short_code = base62.encode(new_id)

    return jsonify({
        "short_code": short_code,
        "short_url": request.host_url + short_code,
        "long_url": long_url
    }), 201


@app.route("/<short_code>")
def redirect_to_long_url(short_code):
    try:
        url_id = base62.decode(short_code)
    except ValueError:
        return jsonify({"error": "Invalid short code"}), 404

    row = db.get_url_by_id(url_id)
    if row is None:
        return jsonify({"error": "Short code not found"}), 404

    db.increment_clicks(url_id)
    return redirect(row["long_url"], code=302)


@app.route("/stats/<short_code>")
def stats(short_code):
    try:
        url_id = base62.decode(short_code)
    except ValueError:
        return jsonify({"error": "Invalid short code"}), 404

    row = db.get_url_by_id(url_id)
    if row is None:
        return jsonify({"error": "Short code not found"}), 404

    return jsonify({
        "short_code": short_code,
        "long_url": row["long_url"],
        "clicks": row["clicks"],
        "created_at": row["created_at"]
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
