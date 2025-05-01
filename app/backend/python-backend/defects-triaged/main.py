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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/defects-triaged")
async def get_defects_triaged(repo: str = Query(...)):
    try:
        # Parse the repo_url to get owner and repo
        parts = repo.strip("/").split("/")
        owner = parts[-2]
        repo = parts[-1]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid repo_url format. Expected format like https://github.com/owner/repo")
    
    repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FastAPI-Metrics-App",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        logger.info(f"Fetching default branch for {owner}/{repo}...")

        # Fetch repo info
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

        # Now, process the defects over the last 90 days
        now = datetime.utcnow()
        past_date = now - timedelta(days=90)  # Manage the dates to consider only the last 90 days

        # Initialize the counters for each day
        open_counts = defaultdict(int)
        closed_counts = defaultdict(int)
        triaged_counts = defaultdict(int)
        matched_label_counts = defaultdict(int)

        severity_counts = {
            "critical": defaultdict(int),
            "high": defaultdict(int),
            "medium": defaultdict(int),
            "low": defaultdict(int)
        }

        # Process each issue and accumulate counts
        for issue in all_issues:
            if "pull_request" in issue:
                continue  # Skip PRs

            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = None
            if issue["state"] == "closed":
                closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
            
            labels = [label["name"].lower() for label in issue.get("labels", [])]
            is_triaged = bool(labels)

            # Update matched_label_counts for triaged labels
            for label in labels:
                if label in TRIAGE_LABELS:
                    matched_label_counts[label] += 1

            # Track issues over the last 90 days
            if created_at >= past_date:
                day = created_at.date().isoformat()
                if issue["state"] == "open":
                    open_counts[day] += 1
                if is_triaged:
                    triaged_counts[day] += 1

            if closed_at and closed_at >= past_date:
                day = closed_at.date().isoformat()
                closed_counts[day] += 1

            # Track severity counts based on labels
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

        # Calculate summary values
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

        # Format the results for the frontend with the summary metrics
        data_by_day = []
        for i in range(90):
            day = (past_date + timedelta(days=i)).date().isoformat()
            data_by_day.append({
                "date": day,
                "open_defects": open_counts.get(day, 0),
                "closed_defects": closed_counts.get(day, 0),
                "triaged_defects": triaged_counts.get(day, 0),
                "critical_severity": severity_counts["critical"].get(day, 0),
                "high_severity": severity_counts["high"].get(day, 0),
                "medium_severity": severity_counts["medium"].get(day, 0),
                "low_severity": severity_counts["low"].get(day, 0)
            })


        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "defect_data": [
                    {"class_name": "Total Defects", "score": total_defects},
                    {"class_name": "Triaged Defects", "score": triaged_defects},
                    {"class_name": "Open Triaged Defects", "score": open_triaged_defects},
                    {"class_name": "Closed Triaged Defects", "score": closed_triaged_defects},
                    {"class_name": "Defect Triaged Percentage", "score": triaged_percentage},
                    {"class_name": "Critical Severity Defects", "score": sum(severity_counts["critical"].values())},
                    {"class_name": "High Severity Defects", "score": sum(severity_counts["high"].values())},
                    {"class_name": "Medium Severity Defects", "score": sum(severity_counts["medium"].values())},
                    {"class_name": "Low Severity Defects", "score": sum(severity_counts["low"].values())},
                ],
                "data_by_day": data_by_day,
                "matched_label_distribution": dict(matched_label_counts)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching triaged defects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error fetching GitHub issues")
