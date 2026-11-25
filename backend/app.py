import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS

from compiler import compile_code

app = Flask(__name__)
CORS(app)


@app.get("/")
def index():
    return jsonify(
        {
            "project": "MiniCompiler Web",
            "status": "ok",
            "message": "Backend listo. Usa POST /api/compile",
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/compile")
def compile_endpoint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "code" not in data:
        return jsonify(
            {
                "success": False,
                "error": {
                    "phase": None,
                    "type": "ERROR DE SOLICITUD",
                    "description": 'El JSON debe incluir la propiedad "code".',
                    "line": None,
                    "column": None,
                },
                "phases": None,
            }
        ), 400

    result = compile_code(data["code"])
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
