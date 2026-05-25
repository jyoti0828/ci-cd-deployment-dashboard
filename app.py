from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from Flask + Docker!",
        "host": socket.gethostname(),
        "env": os.getenv("APP_ENV", "development")
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("APP_ENV") != "production")
