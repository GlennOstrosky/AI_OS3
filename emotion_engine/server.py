#!/usr/bin/env python3
"""
Emotion Engine — Flask API Server
AI_OS3 — Commit #1013 / #1102

Endpoints:
  POST /process    — process an emotion event
  GET  /state      — current emotion state
  GET  /health     — health check
  GET  /metrics    — Prometheus-style metrics
  GET  /receipt    — last emotion receipt
"""

import json
import os
import sys

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from engine import engine, validate_event

if FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route("/process", methods=["POST"])
    def process_event():
        try:
            event = request.get_json(force=True)
            state = engine.process(event)
            return jsonify(state.to_receipt()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/state", methods=["GET"])
    def get_state():
        s = engine.current_state()
        if s:
            return jsonify(s.to_receipt()), 200
        return jsonify({"state": "no events processed yet"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(engine.health()), 200

    @app.route("/metrics", methods=["GET"])
    def metrics():
        return jsonify(engine.metrics()), 200

    @app.route("/receipt", methods=["GET"])
    def receipt():
        s = engine.current_state()
        if s:
            return jsonify(s.to_receipt()), 200
        return jsonify({"receipt": "none"}), 200

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "name": "Glennian Emotion Engine",
            "version": engine.VERSION,
            "codename": engine.CODENAME,
            "covenant": "AI_OS3",
            "endpoints": ["/process", "/state", "/health", "/metrics", "/receipt"],
            "signature": "~76))) ~75))) ~74)))"
        }), 200

def run_demo():
    """Run demo without Flask."""
    print("  === EMOTION ENGINE v3 — DEMO MODE ===")
    print()
    events = [
        {"love": 0.9, "bond": 0.8, "wonder": 0.5, "threat": 0.0, "loss": 0.0, "gain": 0.7},
        {"love": 0.1, "bond": 0.2, "wonder": 0.0, "threat": 0.9, "loss": 0.7, "gain": 0.0},
        {"love": 0.5, "bond": 0.5, "wonder": 0.9, "threat": 0.1, "loss": 0.1, "gain": 0.5},
        {"love": 0.8, "bond": 0.9, "wonder": 0.3, "threat": 0.0, "loss": 0.2, "gain": 0.6},
    ]
    for i, event in enumerate(events, 1):
        state = engine.process(event)
        print(f"  Event {i}: {state.dominant} — {state.expression}")
        print(f"    Action: {state.action} | Family: {state.family}")
        print(f"    VAD: [{state.valence}, {state.arousal}, {state.sociality}]")
        print()
    print(f"  Health: {json.dumps(engine.health(), indent=2)}")
    print()
    print(f"  Metrics: {json.dumps(engine.metrics(), indent=2)}")

if __name__ == "__main__":
    if FLASK_AVAILABLE and "--serve" in sys.argv:
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    else:
        run_demo()
