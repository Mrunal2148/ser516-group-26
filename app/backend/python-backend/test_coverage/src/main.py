from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import clone_repo, run_jacoco, extract_coverage, find_pom_directory
import os

app = Flask(__name__)
CORS(app)

@app.route("/metrics/test-coverage", methods=["GET"])
def get_test_coverage():
    repo_url = request.args.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing GitHub URL"}), 400

    try:
        repo_path = clone_repo(repo_url)
        maven_path = find_pom_directory(repo_path)
        if not maven_path:
            return jsonify({"error": "No pom.xml found in this GitHub repo"}), 400

        success = run_jacoco(maven_path)
        if not success:
            return jsonify({"error": "JaCoCo build or test failed. Likely not a valid Maven Java project."}), 500

        html_path = os.path.join(maven_path, "target", "site", "jacoco", "index.html")
        coverage = extract_coverage(html_path)
        return jsonify({"coverage": coverage, "repo": repo_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
# 