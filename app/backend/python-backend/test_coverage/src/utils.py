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
        subprocess.run([
            "mvn",
            "org.jacoco:jacoco-maven-plugin:0.8.10:prepare-agent",
            "verify"
        ], cwd=path, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def extract_coverage(html_path):
    with open(html_path, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
        cell = soup.find("td", class_="ctr2")
        return cell.text.strip() if cell else "0%"
