"""
Minimal Flask API used as the scan target for this DevSecOps pipeline demo.

This app is intentionally simple — its purpose isn't the application logic,
it's giving Snyk (and the pipeline around it) something real to scan:
outdated Python dependencies, a Dockerfile, and (optionally) Terraform.
"""

from flask import Flask, jsonify
import requests
import yaml

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/echo/<msg>")
def echo(msg):
    return jsonify(message=msg)


@app.route("/config")
def config():
    # Demonstrates the PyYAML dependency being exercised
    sample = yaml.safe_load("service: devsecops-demo\nversion: 1.0")
    return jsonify(sample)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
