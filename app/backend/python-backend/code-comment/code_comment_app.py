import os
import shutil
import subprocess
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import multiprocessing

app = Flask(__name__)
CORS(app)

links_file = 'links.json'

def clone_repo(repo_url: str, repo_path: str):
    """Clone repo with optimizations like shallow clone."""
    if os.path.exists(repo_path):
        try:
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)
            return
        except subprocess.CalledProcessError:
            shutil.rmtree(repo_path)  
    
    subprocess.run(["git", "clone", "--depth=1", repo_url, repo_path], check=True)

def get_code_files(repo_path: str, extensions=None):
    """Retrieve list of relevant code files in repo."""
    if extensions is None:
        extensions = [".py", ".js", ".jsx", ".ts", ".java"]
    code_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                code_files.append(os.path.join(root, file))
    return code_files

def process_file(file_path):
    """Process a single file to calculate comment lines."""
    comment_patterns = {
        ".py": r"^\s*#",
        ".js": r"^\s*//",
        ".jsx": r"^\s*//",
        ".ts": r"^\s*//",
        ".java": r"^\s*//",
    }

    extension = os.path.splitext(file_path)[1]
    if extension not in comment_patterns:
        return 0, 0

    pattern = comment_patterns[extension]
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()
            total_lines = len(lines)
            comment_lines = sum(1 for line in lines if re.match(pattern, line))
            return total_lines, comment_lines
    except Exception:
        return 0, 0  

def calculate_comment_coverage(files):
    """Use multiprocessing to calculate comment coverage faster."""
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_file, files)

    total_lines = sum(result[0] for result in results)
    comment_lines = sum(result[1] for result in results)
    coverage = (comment_lines / total_lines) * 100 if total_lines > 0 else 0
    return total_lines, comment_lines, coverage

def save_to_json(repo_url, total_lines, comment_lines, coverage):
    """Save results to JSON file."""
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
    """Analyze repository for comment coverage."""
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
    """Fetch stored coverage data."""
    file_path = "coverage_data.json"

    if not os.path.exists(file_path):
        return jsonify([])

    with open(file_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5006)
