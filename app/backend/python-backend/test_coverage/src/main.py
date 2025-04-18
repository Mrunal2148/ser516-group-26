from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import safe_join
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

        # Locate pom.xml
        pom_dir = None
        for root, _, files in os.walk(temp_dir):
            if "pom.xml" in files:
                pom_dir = root
                break

        # Inject default pom.xml if not found
        if not pom_dir:
            print("⚠️ No pom.xml found, injecting default")
            pom_dir = temp_dir
            templates_dir = os.path.join(os.getcwd(), "templates")
            default_pom = os.path.join(templates_dir, "default_pom.xml")
            if not os.path.exists(default_pom):
                return jsonify({"error": "Default pom.xml template not found."}), 500
            shutil.copy(default_pom, os.path.join(pom_dir, "pom.xml"))

        # Run Maven tests to generate JaCoCo report
        subprocess.run(["mvn", "clean", "test"], cwd=pom_dir, check=True)

        report_path = os.path.join(pom_dir, "target", "site", "jacoco", "index.html")
        if not os.path.exists(report_path):
            # Try explicit report generation
            subprocess.run([
                "mvn",
                "org.jacoco:jacoco-maven-plugin:0.8.10:prepare-agent",
                "test",
                "org.jacoco:jacoco-maven-plugin:0.8.10:report"
            ], cwd=pom_dir, check=True)

        if not os.path.exists(report_path):
            return jsonify({"error": "JaCoCo report not found."}), 500

        # Copy report to /tmp for frontend download
        report_copy_dir = "/tmp/test_coverage_output"
        os.makedirs(report_copy_dir, exist_ok=True)
        dest_path = os.path.join(report_copy_dir, "test_coverage_report.html")
        shutil.copytree(
           os.path.dirname(report_path),  # the entire /jacoco/ folder
            "/tmp/test_coverage_output",
            dirs_exist_ok=True
        )

        return jsonify({
            "message": "Report generated successfully",
            "download_path": "/metrics/test-coverage-report"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Maven command failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route("/metrics/test-coverage-report", methods=["GET"])
def serve_test_coverage_report():
    return send_file("/tmp/test_coverage_output/index.html")

@app.route("/metrics/jacoco-resources/<path:filename>")
def serve_jacoco_resources(filename):
    resource_dir = "/tmp/test_coverage_output/jacoco-resources"
    full_path = safe_join(resource_dir, filename)
    if os.path.exists(full_path):
        return send_from_directory(resource_dir, filename)
    else:
        return "Resource not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
