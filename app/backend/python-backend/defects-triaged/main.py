from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os
from datetime import datetime, timedelta
from collections import defaultdict

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

TRIAGE_LABELS = {
    "triaged", "bug", "defect", "type: bug", "type: defect",
    "severity: high", "severity: low", "critical", "blocker",
    "high", "medium", "low",
    "priority: high", "priority: medium", "priority: low",
    "severity: critical", "severity: major", "severity: minor", "severity: trivial"
}

SEVERITY_LABELS = {
    "critical", "blocker",
    "high", "medium", "low",
    "priority: high", "priority: medium", "priority: low",
    "severity: critical", "severity: major", "severity: minor", "severity: trivial"
}

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

        all_issues = []
        page = 1
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
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

        # New Part
        now = datetime.utcnow()
        past_date = now - timedelta(days=90)  # here we are manageing the dates

        open_counts = defaultdict(int)
        closed_counts = defaultdict(int)
        triaged_counts = defaultdict(int)

        severity_counts = {
            "critical": defaultdict(int),
            "high": defaultdict(int),
            "medium": defaultdict(int),
            "low": defaultdict(int)
        }
        matched_label_counts = defaultdict(int)  # Key = known label, Value = number of issues with that label

        for issue in all_issues:
            if "pull_request" in issue:
                continue  # Skip PRs

            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = None
            if issue["state"] == "closed":
                closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
            
            labels = [label["name"].lower() for label in issue.get("labels", [])]
            is_triaged = bool(labels)

            if created_at >= past_date:
                day = created_at.date().isoformat()
                if issue["state"] == "open":
                    open_counts[day] += 1
                if is_triaged:
                    triaged_counts[day] += 1

            if closed_at and closed_at >= past_date:
                day = closed_at.date().isoformat()
                closed_counts[day] += 1

            for label in labels:
                if label in TRIAGE_LABELS:
                    matched_label_counts[label] += 1

            for label in labels:
                if label in SEVERITY_LABELS:
                    if "critical" in label or "blocker" in label:
                        severity_counts["critical"][day] += 1
                    elif "high" in label:
                        severity_counts["high"][day] += 1
                    elif "medium" in label:
                        severity_counts["medium"][day] += 1
                    elif "low" in label:
                        severity_counts["low"][day] += 1

        # Calculate the summary values
        total_defects = sum(open_counts.values()) + sum(closed_counts.values())
        triaged_defects = sum(triaged_counts.values())

        open_triaged_defects = 0
        closed_triaged_defects = 0

        for issue in all_issues:
            if "pull_request" in issue:
                continue
            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = None
            if issue["state"] == "closed":
                closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
            
            labels = [label["name"].lower() for label in issue.get("labels", [])]
            is_triaged = bool(labels)

            if created_at >= past_date and issue["state"] == "open" and is_triaged:
                open_triaged_defects += 1
            if closed_at and closed_at >= past_date and is_triaged:
                closed_triaged_defects += 1

        # Now calculate triaged percentage
        triaged_percentage = int((triaged_defects / total_defects) * 100) if total_defects else 0


        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": [
                {"class_name": "Total Defects", "score": total_defects},
                {"class_name": "Triaged Defects", "score": triaged_defects},
                {"class_name": "Open Triaged Defects", "score": open_triaged_defects},
                {"class_name": "Closed Triaged Defects", "score": closed_triaged_defects},
                {"class_name": "Defect Triaged Percentage", "score": triaged_percentage},
                {"class_name": "Critical Severity Defects", "score": severity_counts["critical"]},
                {"class_name": "High Severity Defects", "score": severity_counts["high"]},
                {"class_name": "Medium Severity Defects", "score": severity_counts["medium"]},
                {"class_name": "Low Severity Defects", "score": severity_counts["low"]},
            ],
            "matched_label_distribution": dict(matched_label_counts)
        }

    except Exception as e:
        logger.error(f"Error fetching triaged defects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error fetching GitHub issues")
