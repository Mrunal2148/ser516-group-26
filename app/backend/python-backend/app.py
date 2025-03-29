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

def clone_repo(repo_url: str, repo_path: str):
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    subprocess.run(["git", "clone", repo_url, repo_path], check=True)

def get_code_files(repo_path: str, extensions=None):
    if extensions is None:
        extensions = [".py", ".js", ".jsx", ".ts", ".java"]
    code_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                code_files.append(os.path.join(root, file))
    return code_files

def calculate_comment_coverage(files):
    total_lines = 0
    comment_lines = 0
    comment_patterns = {
        ".py": r"^\s*#",
        ".js": r"^\s*//",
        ".jsx": r"^\s*//",
        ".ts": r"^\s*//",
        ".java": r"^\s*//",
    }
    for file_path in files:
        extension = os.path.splitext(file_path)[1]
        if extension not in comment_patterns:
            continue
        pattern = comment_patterns[extension]
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()
            total_lines += len(lines)
            comment_lines += sum(1 for line in lines if re.match(pattern, line))

    coverage = (comment_lines / total_lines) * 100 if total_lines > 0 else 0
    return total_lines, comment_lines, coverage

def save_to_json(repo_url, total_lines, comment_lines, coverage):
    data = {
        "repo_url": repo_url,
        "total_lines": total_lines,
        "comment_lines": comment_lines,
        "coverage": coverage,
        "timestamp": datetime.utcnow().isoformat()
    }

    file_path = "coverage_data.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(file_path, "w") as f:
        json.dump(existing_data, f, indent=4)

@app.route("/analyze", methods=["POST"])
def analyze_repository():
    data = request.get_json()
    repo_url = data.get("repo_url")

    if not repo_url:
        return jsonify({"error": "GitHub repository URL is required"}), 400

    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = f"/tmp/{repo_name}"

    try:
        clone_repo(repo_url, repo_path)
        code_files = get_code_files(repo_path)
        total_lines, comment_lines, coverage = calculate_comment_coverage(code_files)

        save_to_json(repo_url, total_lines, comment_lines, coverage)

        shutil.rmtree(repo_path)

        return jsonify({"coverage": coverage})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/get_coverage_data", methods=["GET"])
def get_coverage_data():
    file_path = "coverage_data.json"

    if not os.path.exists(file_path):
        return jsonify([])

    with open(file_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    return jsonify(data)

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