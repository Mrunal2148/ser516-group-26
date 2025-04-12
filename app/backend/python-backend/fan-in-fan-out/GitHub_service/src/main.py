from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import zipfile
import tempfile
import os
import shutil
import json
from typing import List, Dict, Any, Optional
import logging
import traceback
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("github_service")

app = FastAPI(
    title="GitHub Service",
    description="Service for fetching Java repositories from GitHub",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API_BASE_URL = "https://api.github.com"
FAN_IN_SERVICE_URL = "http://localhost:8001/metrics/fan-in"
FAN_OUT_SERVICE_URL = "http://localhost:8002/metrics/fan-out"


@app.post("/github-zip")
async def github_zip(githubZipUrl: str = Form(...)):
    try:
        # Extract owner and repo from the GitHub URL
        parts = githubZipUrl.replace("https://github.com/", "").split("/")
        owner = parts[0]
        repo = parts[1] if len(parts) > 1 else ""
        
        # Call the existing fetch-repo endpoint
        repo_details = {
            "owner": owner,
            "repo": repo,
            "branch": "master"  # Default to master, could be main too
        }
        
        fetch_result = await fetch_repo(repo_details)
        zip_path = fetch_result.get("zip_path")
        
        # Get the file listing for Java files in the ZIP
        with open(zip_path, 'rb') as f:
            files = {'folder': (os.path.basename(zip_path), f, 'application/zip')}
            response = requests.post("http://localhost:8001/upload-folder", files=files)
            response.raise_for_status()
            file_list_result = response.json()
        
        return {
            "files": file_list_result.get("files", []),
            "zipFileName": os.path.basename(zip_path)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing GitHub ZIP: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process GitHub ZIP: {str(e)}")

@app.get("/")
async def root():
    return {"message": "GitHub Service with JavaParser Integration for Metrics Calculation"}

@app.get("/health")
async def health_check():
    jvm_status = "initialized" if 'jpype' in globals() and jpype.isJVMStarted() else "not initialized"
    return {
        "status": "healthy",
        "javaparser": jvm_status
    }

@app.post("/fetch-repo")
async def fetch_repo(
    repo_details: Dict[str, str] = Body(
        ...,
        example={
            "owner": "username",
            "repo": "repository-name",
            "branch": "",
            "token": "github_personal_access_token", # Optional
            "path": "", # Optional, specific directory in the repo
        }
    )
):
    try:
        # Clear any previous temporary files with similar names
        owner = repo_details.get("owner")
        repo = repo_details.get("repo")
        branch = repo_details.get("branch")
        token = repo_details.get("token")
        path = repo_details.get("path", "")
        
        if not branch:
            repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {"Authorization": f"token {token}"} if token else {}
            response = requests.get(repo_info_url, headers=headers)
            if response.status_code == 200:
                branch = response.json().get("default_branch", "main")
                logger.info(f"Using default branch: {branch}")
            else:
                logger.warning(f"Could not fetch default branch, defaulting to 'main'")
                branch = "main"

        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")
        
        # Clean up any existing ZIP files for this or other repositories
        temp_dir = tempfile.gettempdir()
        for old_file in os.listdir(temp_dir):
            if old_file.endswith(".zip") and os.path.isfile(os.path.join(temp_dir, old_file)):
                try:
                    os.remove(os.path.join(temp_dir, old_file))
                    logger.info(f"Removed old zip file: {old_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove old zip file {old_file}: {str(e)}")
        
        # Create a new temporary directory
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")
        
        java_files = []
        fetch_error = None
        
        # If branch is not specified, try both main and master
        branches_to_try = [branch] if branch else ["main", "master"]
        
        for branch_name in branches_to_try:
            try:
                logger.info(f"Attempting to fetch repository with branch: {branch_name}")
                java_files = await fetch_java_files(
                    owner=owner,
                    repo=repo,
                    branch=branch_name,
                    token=token,
                    path=path,
                    output_dir=temp_dir
                )
                if java_files:
                    # If we found files, use this branch and break the loop
                    branch = branch_name
                    break
            except Exception as e:
                fetch_error = str(e)
                logger.warning(f"Failed to fetch with branch {branch_name}: {str(e)}")
                # Continue to try next branch if available
        
        if not java_files:
            shutil.rmtree(temp_dir)
            raise HTTPException(status_code=404, detail="No Java files found in the repository")
        
        zip_path = os.path.join(tempfile.gettempdir(), f"{owner}_{repo}_{branch}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in java_files:
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
        
        shutil.rmtree(temp_dir)
        logger.info(f"Created ZIP file at {zip_path}")
        
        return {
            "status": "success",
            "message": f"Repository {owner}/{repo} fetched successfully",
            "zip_path": zip_path,
            "file_count": len(java_files)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching repository: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository: {str(e)}")

async def fetch_java_files(
    owner: str, 
    repo: str, 
    branch: str, 
    token: Optional[str], 
    path: str,
    output_dir: str
) -> List[str]:
    java_files = []
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/{path}"
    if branch:
        url += f"?ref={branch}"
    logger.info(f"Fetching repository contents from: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch repository contents: {response.status_code} - {response.text}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"GitHub API error: {response.json().get('message', 'Unknown error')}"
        )
    contents = response.json()
    if not isinstance(contents, list):
        contents = [contents]
    for item in contents:
        item_path = item.get("path")
        item_type = item.get("type")
        if item_type == "dir":
            nested_path = item.get("path", "")
            nested_files = await fetch_java_files(
                owner=owner,
                repo=repo,
                branch=branch,
                token=token,
                path=nested_path,
                output_dir=output_dir
            )
            java_files.extend(nested_files)
        elif item_type == "file" and item_path.endswith(".java"):
            download_url = item.get("download_url")
            if not download_url:
                content_base64 = item.get("content", "")
                content = base64.b64decode(content_base64).decode("utf-8")
            else:
                file_response = requests.get(download_url, headers=headers)
                if file_response.status_code != 200:
                    logger.warning(f"Failed to download file {item_path}: {file_response.status_code}")
                    continue
                content = file_response.text
            rel_path = item_path
            file_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            java_files.append(file_path)
    return java_files

@app.get("/download")
async def download_zip(path: str = Query(..., description="Path to the ZIP file")):
    if not os.path.exists(path):
        return {"error": "ZIP file not found"}

    return FileResponse(path, filename=os.path.basename(path), media_type="application/zip")

@app.post("/analyze-repo")
async def analyze_repo(
    repo_details: Dict[str, Any] = Body(
        ...,
        example={
            "owner": "username",
            "repo": "repository-name",
            "branch": "main",
            "token": "github_personal_access_token", # Optional
            "path": "", # Optional, specific directory in the repo
            "function_name": "target" # Required for fan-in, and fan-out.
        }
    )
):
    try:
        fetch_result = await fetch_repo(repo_details)
        zip_path = fetch_result.get("zip_path")
        function_name = repo_details.get("function_name")
        owner = repo_details.get("owner")
        repo = repo_details.get("repo")
        branch = repo_details.get("branch")
        path = repo_details.get("path")

        if not zip_path or not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Failed to create ZIP file from repository")

        if not function_name:
            raise HTTPException(status_code=400, detail="Function name is required for analysis")

        logger.info(f"ZIP file created at: {zip_path}")
        logger.info(f"Owner: {owner}, Repo: {repo}, Branch: {branch}, Path: {path}")

        try:
            # Call the file listing service
            with open(zip_path, 'rb') as f:
                files = {'folder': (os.path.basename(zip_path), f, 'application/zip')}
                response = requests.post("http://localhost:8001/upload-folder", files=files)
                logger.info(f"File listing service response: {response.status_code} - {response.text}") # Log the full response

                response.raise_for_status() # Raise exception for bad status codes
                file_list_result = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling file listing service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get file list from ZIP: {str(e)}")

        # ... (rest of your analyze-repo logic)

        fan_in_result = await call_fan_in_service(zip_path, function_name)
        fan_out_result = await call_fan_out_service(zip_path, function_name)

        return {
            "status": "success",
            "message": "Repository fetched and analyzed successfully",
            "zip_path": zip_path,
            "file_count": fetch_result.get("file_count"),
            "fan_in_result": fan_in_result,
            "fan_out_result": fan_out_result,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error analyzing repository: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze repository: {str(e)}")

async def call_fan_in_service(zip_path: str, function_name: str):
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {'function_name': function_name}
            response = requests.post(FAN_IN_SERVICE_URL, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling fan-in service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to call fan-in service: {str(e)}")

async def call_fan_out_service(zip_path: str, function_name:str):
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {'function_name': function_name}
            response = requests.post(FAN_OUT_SERVICE_URL, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling fan-out service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to call fan-out service: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)