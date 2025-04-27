from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os
import zipfile
import shutil
import tempfile
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("defects-triaged-service")

app = FastAPI(
    title="Defects Triaged Service",
    description="Service for calculating the number of defects triaged in a GitHub repo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TRIAGE_LABELS = {"triaged", "bug", "defect", "type: bug", "type: defect", "severity: high", "severity: low"}

@app.get("/")
async def root():
    return {"message": "Defects Triaged Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics/defects-triaged")
async def get_defects_triaged(owner: str = Query(...), repo: str = Query(...)):
    repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FastAPI-Metrics-App",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        # Get default branch
        logger.info(f"Fetching default branch for {owner}/{repo}...")
        repo_info = requests.get(repo_api_url, headers=headers)
        if repo_info.status_code != 200:
            raise HTTPException(status_code=repo_info.status_code, detail="Failed to fetch repo info")

        default_branch = repo_info.json().get("default_branch", "main")
        logger.info(f"Default branch is '{default_branch}'")

        # Fetch issues
        base_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        all_issues = []
        page = 1
        while True:
            response = requests.get(
                base_url,
                headers=headers,
                params={"state": "all", "per_page": 100, "page": page}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="GitHub API error")

            page_issues = response.json()
            if not page_issues:
                break

            all_issues.extend(page_issues)
            page += 1

        total_defects = 0
        triaged_defects = 0
        open_defects = 0
        closed_defects = 0

        severity_counts = {"critical": 0, "major": 0, "minor": 0}

        for issue in all_issues:
            if "pull_request" in issue:
                continue

            labels = [label["name"].lower() for label in issue.get("labels", [])]
            total_defects += 1

            is_triaged = any(label in TRIAGE_LABELS for label in labels)
            if is_triaged:
                triaged_defects += 1
                if issue["state"] == "open":
                    open_defects += 1
                elif issue["state"] == "closed":
                    closed_defects += 1

            triaged_percentage = int((triaged_defects / total_defects) * 100) if total_defects else 0


        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": [
                {"class_name": "Total Defects", "score": total_defects},
                {"class_name": "Triaged Defects", "score": triaged_defects},
                {"class_name": "Open Triaged Defects", "score": open_defects},
                {"class_name": "Closed Triaged Defects", "score": closed_defects},
                {"class_name": "Defect Triaged Percentage", "score": triaged_percentage}
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching triaged defects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error fetching GitHub issues")