import git
import os
import tempfile
import subprocess
from bs4 import BeautifulSoup

def clone_repo(github_url):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(github_url, temp_dir)
    return temp_dir

def find_pom_directory(path):
    for root, dirs, files in os.walk(path):
        if "pom.xml" in files:
            return root
    return None

def run_jacoco(path):
    try:
        result = subprocess.run(
            ["mvn", "verify"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print("✅ Maven STDOUT:", result.stdout.decode())
        print("✅ Maven STDERR:", result.stderr.decode())
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Maven Build Failed!")
        print("STDOUT:", e.stdout.decode() if e.stdout else "N/A")
        print("STDERR:", e.stderr.decode() if e.stderr else "N/A")
        return False

def extract_coverage(html_path):
    try:
        with open(html_path, "r") as f:
            soup = BeautifulSoup(f, "html.parser")

            table = soup.find("table", class_="coverage")
            if not table:
                return "0%"

            rows = table.find_all("tr")
            if len(rows) < 2:
                return "0%"

            data_cells = rows[1].find_all("td", class_="ctr2")
            if not data_cells:
                return "0%"

            return data_cells[0].text.strip()
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return "0%"
