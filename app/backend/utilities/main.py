from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import subprocess
import shutil
from bs4 import BeautifulSoup
from datetime import datetime

# Added: Common utility imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from .utilities.fetch_repo import fetch_repo, get_owner_repo
from .utilities.response_wrapper import wrap_with_timestamp

app = Flask(__name__)
CORS(app)

@app.route("/metrics/test-coverage", methods=["GET"])
def test_coverage():
    repo_url = request.args.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing repo URL"}), 400

    # Use fetch_repo instead of direct clone
    try:
        fetch_res = fetch_repo(repo_url)
        if isinstance(fetch_res, dict) and "error" in fetch_res:
            return jsonify({"error": fetch_res["error"]}), 400

        head_sha, temp_dir = fetch_res

        # COMMENTED OUT: Old manual clone logic
        # temp_dir = tempfile.mkdtemp()
        # if "https://github.com" in repo_url and GITHUB_TOKEN:
        #     tokenized_url = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@")
        # else:
        #     tokenized_url = repo_url
        # git.Repo.clone_from(tokenized_url, temp_dir)

        # Locate or inject pom.xml
        pom_dir = None
        for root, _, files in os.walk(temp_dir):
            if "pom.xml" in files:
                pom_dir = root
                break

        if not pom_dir:
            print("⚠️ No pom.xml found, injecting default")
            pom_dir = temp_dir
            templates_dir = os.path.join(os.getcwd(), "templates")
            default_pom = os.path.join(templates_dir, "default_pom.xml")
            if not os.path.exists(default_pom):
                return jsonify({"error": "Default pom.xml template not found."}), 500
            shutil.copy(default_pom, os.path.join(pom_dir, "pom.xml"))

        # Run Maven tests with JaCoCo
        subprocess.run([
            "mvn",
            "clean",
            "org.jacoco:jacoco-maven-plugin:0.8.10:prepare-agent",
            "test",
            "org.jacoco:jacoco-maven-plugin:0.8.10:report"
        ], cwd=pom_dir, check=True)

        report_dir = os.path.join(pom_dir, "target", "site", "jacoco")
        index_path = os.path.join(report_dir, "index.html")
        if not os.path.exists(index_path):
            return jsonify({"error": "JaCoCo report not found."}), 500

        output_dir = "/tmp/test_coverage_output"
        os.makedirs(output_dir, exist_ok=True)
        shutil.copytree(report_dir, output_dir, dirs_exist_ok=True)

        # Class-level parsing ===
        data = []
        with open(index_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        coverage_table = soup.find("table", class_="coverage")
        if not coverage_table:
            return jsonify({"error": "Coverage table not found in index.html"}), 500

        for row in coverage_table.find("tbody").find_all("tr"):
            cells = row.find_all("td")
            if len(cells) > 0:
                link = cells[0].find("a")
                if link and "href" in link.attrs:
                    subpage_path = link['href']
                    subpage_file = os.path.join(report_dir, subpage_path)
                    package_name = subpage_path.replace("/index.html", "").replace("/", ".")

                    if os.path.exists(subpage_file):
                        with open(subpage_file, "r", encoding="utf-8") as sf:
                            sub_soup = BeautifulSoup(sf, "html.parser")
                        sub_table = sub_soup.find("table", class_="coverage")
                        if not sub_table:
                            continue

                        for sub_row in sub_table.find("tbody").find_all("tr"):
                            sub_cells = sub_row.find_all("td")
                            if len(sub_cells) >= 3:
                                file_name = sub_cells[0].text.strip()
                                class_name = file_name.replace(".java", "").replace(".kt", "")
                                full_class_name = f"{package_name}.{class_name}"

                                try:
                                    score = int(sub_cells[2].text.strip().replace('%', ''))
                                except:
                                    score = 0

                                data.append({
                                    "class_name": full_class_name,
                                    "score": score
                                })

        #Use wrap_with_timestamp for response consistency
        return jsonify(wrap_with_timestamp({"data": data}))

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Maven command failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
