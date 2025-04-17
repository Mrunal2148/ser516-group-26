from flask import Flask, request, jsonify, send_file
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

        # Copy report to Downloads folder
        downloads_path = os.path.expanduser("~/Downloads")
        dest_path = os.path.join(downloads_path, "test_coverage_report.html")
        shutil.copy(report_path, dest_path)

        return jsonify({
            "message": "Report downloaded to your Downloads folder",
            "download_path": "/downloads/test_coverage_report.html"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
