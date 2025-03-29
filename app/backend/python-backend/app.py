import os
import shutil
import subprocess
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

links_file = 'links.json'

def read_links():
    if os.path.exists(links_file):
        with open(links_file, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return [] 
    return []

def save_links(links):
    try:
        with open(links_file, 'w') as file:
            json.dump(links, file, indent=4)
    except Exception as e:
        print("Error writing to file:", e)

@app.route('/links.json', methods=['GET'])
def get_links():
    links = read_links()
    return jsonify(links)

@app.route('/save-links', methods=['POST'])
def save_new_links():
    data = request.get_json()
    if not isinstance(data, list):  
        return jsonify({"error": "Invalid data format, expected a list"}), 400

    save_links(data)  
    return jsonify({"message": "Links saved successfully!"}), 200

@app.route("/save-benchmark", methods=["POST"])
def save_benchmark():
    data = request.get_json()
    repo_url = data.get("repoUrl")
    metric = data.get("metric")
    history_entry = data.get("history")[0]


    if not repo_url or not metric or not history_entry:
        return jsonify({"error": "Invalid data"}), 400


    benchmark_file = "benchmarks.json"


    if os.path.exists(benchmark_file):
        with open(benchmark_file, "r") as f:
            try:
                benchmarks = json.load(f)
            except json.JSONDecodeError:
                benchmarks = []
    else:
        benchmarks = []


    
    for benchmark in benchmarks:
        if benchmark["repoUrl"] == repo_url and benchmark["metric"] == metric:
            benchmark["history"].append(history_entry)
            break
    else:
        
        benchmarks.append({
            "repoUrl": repo_url,
            "metric": metric,
            "history": [history_entry]
        })


    with open(benchmark_file, "w") as f:
        json.dump(benchmarks, f, indent=4)


    return jsonify({"message": "Benchmark saved successfully!"}), 200

@app.route("/benchmarks.json", methods=["GET"])
def get_benchmarks():
    benchmark_file = "benchmarks.json"
    if os.path.exists(benchmark_file):
        with open(benchmark_file, "r") as file:
            try:
                benchmarks = json.load(file)
                return jsonify(benchmarks), 200
            except json.JSONDecodeError:
                return jsonify({"error": "Failed to read benchmarks.json"}), 500
    return jsonify([]), 200
 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)