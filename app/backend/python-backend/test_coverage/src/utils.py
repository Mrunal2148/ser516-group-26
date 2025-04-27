import os
import shutil
import subprocess
import tempfile
from pathlib import Path

def run_coverage(github_url):
    repo_name = github_url.split("/")[-1].replace(".git", "")
    temp_dir = tempfile.mkdtemp()

    try:
        subprocess.run(["git", "clone", github_url, temp_dir], check=True)
    except subprocess.CalledProcessError:
        return {"error": "❌ Failed to clone repository."}

    pom_path = os.path.join(temp_dir, "pom.xml")
    if not os.path.exists(pom_path):
        try:
            template_path = os.path.join(os.getcwd(), "templates", "default_pom.xml")
            shutil.copy(template_path, pom_path)
        except Exception as e:
            return {"error": f"❌ Failed to inject pom.xml: {e}"}

    try:
        subprocess.run(["mvn", "clean", "test"], cwd=temp_dir, check=True)
    except subprocess.CalledProcessError:
        return {"error": "❌ Maven test execution failed."}

    report_dir = Path(temp_dir) / "target" / "site" / "jacoco"
    if report_dir.exists():
        output_dir = os.path.join(os.getcwd(), "downloads", repo_name)
        os.makedirs(output_dir, exist_ok=True)
        shutil.copytree(report_dir, output_dir, dirs_exist_ok=True)
        return {"success": True, "report_path": f"/downloads/{repo_name}/index.html"}
    else:
        return {"error": "❌ JaCoCo report not found."}
