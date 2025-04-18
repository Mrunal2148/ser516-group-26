from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os 

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
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FastAPI-Metrics-App",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        response = requests.get(url, headers=headers, params={"state": "all", "per_page": 100})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="GitHub API error")

        issues = response.json()

        total_defects = 0
        triaged_defects = 0
        open_defects = 0
        closed_defects = 0

        severity_counts = {
            "critical": 0,
            "major": 0,
            "minor": 0
        }

        for issue in issues:
            # Ignore pull requests
            if "pull_request" in issue:
                continue

            labels = [label["name"].lower() for label in issue.get("labels", [])]

            # Check if it's a defect
            is_defect = any(label in {"bug", "defect", "type: bug", "type: defect"} for label in labels)
            if not is_defect:
                continue

            total_defects += 1

            # Check triaged status
            is_triaged = any(label in {"triaged", "severity: high", "severity: low", "severity: medium"} for label in labels)
            if is_triaged:
                triaged_defects += 1

            # Severity classification
            if "severity: high" in labels or "critical" in labels:
                severity_counts["critical"] += 1
            elif "severity: medium" in labels or "major" in labels:
                severity_counts["major"] += 1
            elif "severity: low" in labels or "minor" in labels:
                severity_counts["minor"] += 1

            # Status
            if issue["state"] == "open":
                open_defects += 1
            elif issue["state"] == "closed":
                closed_defects += 1

        triaged_percentage = int((triaged_defects / total_defects) * 100) if total_defects else 0

        return {
            "total_defects": total_defects,
            "triaged_defects": triaged_defects,
            "triaged_percentage": triaged_percentage,
            "by_severity": severity_counts,
            "open_defects": open_defects,
            "closed_defects": closed_defects
        }

    except Exception as e:
        logger.error(f"Error fetching triaged defects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error fetching GitHub issues")
