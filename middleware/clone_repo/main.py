import os
from clone_repo import clone_repo
import config
from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

def load_service_config():
    services = config.services_list
    service_mapping = {}
    for service in services:
        service_mapping[os.getenv(f"{service}_PORT")] = os.getenv(f"{service}_NAME")
    return service_mapping

def fetch_metrics(name, port, payload):
    try:
        url = f"{config.endpoint_prefix}{name}_api:{port}/{name}"
        response = requests.post(url, json=payload)
        return name, response.json()
    except Exception as e:
        return name, {"error": str(e)}

@app.route("/metrics", methods=["POST"])
def get_metrics():
    try:
        data = request.get_json()
        repo_url = data["repo_url"]
        head_sha, repo_dir = clone_repo(repo_url)

        services = load_service_config()
        payload = {config.payload_key: repo_url}

        results = {}
        with ThreadPoolExecutor(max_workers=len(services)) as executor:
            futures = [executor.submit(fetch_metrics, name, port, payload) for port, name in services.items()]
            for future in as_completed(futures):
                name, result = future.result()
                results[name] = result

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"message": f"Error occurred while cloning repository or fetching metrics: {e}"}), 500
    
@app.route("/metrics-group-6", methods=["POST"])
def get_metrics_grp_6():
    try:
        data = request.get_json()
        repo_url = data["repo_url"]
        head_sha, repo_dir = clone_repo(repo_url)

        payload = {config.payload_key: repo_url}
        results = {}
        code_comment_res = requests.post("http://code-comment-coverage:5006/api/github/code-comment-coverage", json=payload)
        results["code-comment-coverage"] = code_comment_res.json()
        return jsonify({"results": results}), 200
        
    except Exception as e:
        return jsonify({"message": f"Error occurred while cloning repository or fetching metrics: {e}"}), 500

@app.route("/metrics-fogindex", methods=["POST"])
def get_metrics_fogindex():
    try:
        data = request.get_json()
        repo_url = data["repo_url"]
        head_sha, repo_dir = clone_repo(repo_url)

        payload = {config.payload_key: repo_url}
        results = {}
        fog_index = requests.post("http://fogindex:5000/fog-index/calculate", json=payload)
        results["fog-index"] = fog_index.json()
        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"message": f"Error occurred while cloning repository or fetching metrics: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)