import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from app.api.system import system_bp
from app.api.production import production_bp

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

app.register_blueprint(system_bp, url_prefix='/api/v1')
app.register_blueprint(production_bp, url_prefix='/api/v1/prod')

@app.route("/")
def read_root():
    return jsonify({"message": "Welcome to Human Agent API"})

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8100))
    app.run(host="0.0.0.0", port=port, debug=True)
