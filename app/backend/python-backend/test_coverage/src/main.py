from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import subprocess
import git
import shutil

app = Flask(__name__)
CORS(app)

@app.route("/metrics/test-coverage", methods=["GET"])
def test_coverage():
    repo_url = request.args.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing repo URL"}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(repo_url, temp_dir)

        # Find pom.xml
        pom_dir = None
        for root, _, files in os.walk(temp_dir):
            if "pom.xml" in files:
                pom_dir = root
                break

        if not pom_dir:
            return jsonify({"error": "No pom.xml found"}), 400

        subprocess.run(["mvn", "verify"], cwd=pom_dir, check=True)

        report_path = os.path.join(pom_dir, "target", "site", "jacoco", "index.html")
        if not os.path.exists(report_path):
            subprocess.run([
                "mvn",
                "org.jacoco:jacoco-maven-plugin:0.8.10:prepare-agent",
                "test",
                "org.jacoco:jacoco-maven-plugin:0.8.10:report"
            ], cwd=pom_dir, check=True)

        if not os.path.exists(report_path):
            return jsonify({"error": "JaCoCo report not found"}), 500

        # Copy report to safe internal path
        report_copy_dir = "/tmp/test_coverage_output"
        os.makedirs(report_copy_dir, exist_ok=True)
        dest_path = os.path.join(report_copy_dir, "test_coverage_report.html")
        shutil.copy(report_path, dest_path)

        return jsonify({
            "message": "Report generated successfully",
            "download_path": "/metrics/test-coverage-report"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/metrics/test-coverage-report", methods=["GET"])
def serve_test_coverage_report():
    report_dir = "/tmp/test_coverage_output"
    file_path = os.path.join(report_dir, "test_coverage_report.html")
    if os.path.exists(file_path):
        return send_from_directory(directory=report_dir, path="test_coverage_report.html")
    else:
        return "Report not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
