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
import base64
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
#trying to send it to fan in out directly
FAN_IN_SERVICE_URL = "http://localhost:8001/metrics/fan-in"
FAN_OUT_SERVICE_URL = "http://localhost:8002/metrics/fan-out"
#FAN_IN_SERVICE_URL = "http://fan-in-service:8001/metrics/fan-in"
#FAN_OUT_SERVICE_URL = "http://fan-out-service:8002/metrics/fan-out"

def get_default_branch(owner: str, repo: str, token: str = None) -> str:
    """
    Retrieves the default branch for a GitHub repository.
    """
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["default_branch"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get default branch for {owner}/{repo}: {e}")
        raise HTTPException(status_code=response.status_code if isinstance(e, requests.exceptions.HTTPError) else 500,
                            detail=f"Failed to get default branch: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Unexpected response format from GitHub API: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected response from GitHub API: {e}")

def download_github_zip(owner: str, repo: str, branch: str = None, token: str = None) -> str:
    """
    Downloads a GitHub repository as a ZIP archive.
    """
    if not branch:
        branch = get_default_branch(owner, repo, token)

    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    logger.info(f"Downloading ZIP archive from: {zip_url}")

    headers = {"Authorization": f"token {token}"} if token else {}
    try:
        response = requests.get(zip_url, headers=headers, stream=True) # stream=True for large files
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        try:
            message = response.json().get("message", "Unknown error")
        except:
            message = str(response.content[:200])
        raise HTTPException(status_code=response.status_code if isinstance(e, requests.exceptions.HTTPError) else 500, detail=f"Failed to download ZIP archive: {message}")

    zip_path = os.path.join(tempfile.gettempdir(), f"{owner}_{repo}_{branch}.zip")
    try:
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):  # Stream in chunks
                f.write(chunk)

        logger.info(f"ZIP archive saved to: {zip_path}")
        return zip_path
    except Exception as e:
        logger.error(f"Error saving ZIP archive to disk: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving ZIP archive: {e}")

@app.post("/fetch-repo")
async def fetch_repo(
    repo_details: Dict[str, str] = Body(
        ...,
        example={
            "owner": "username",
            "repo": "repository-name",
            "branch": "",
            "token": "github_personal_access_token", # Not Optional
            "path": "", # Optional, specific directory in the repo
        }
    )
):
    try:
        owner = repo_details.get("owner")
        repo = repo_details.get("repo")
        branch = repo_details.get("branch")
        token = repo_details.get("token")
        path = repo_details.get("path", "")
        
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
        
        # Create a new temporary directory - but not used now
        # temp_dir = tempfile.mkdtemp()
        # logger.info(f"Created temporary directory: {temp_dir}")

        try:
            zip_path = download_github_zip(owner, repo, branch, token)
        except HTTPException as e:
            raise e # Re-raise the exception
        
        #shutil.rmtree(temp_dir)  # Clean up the temporary directory (if it was created)  #<----- Not used now

        return {
            "status": "success",
            "message": f"Repository {owner}/{repo} fetched successfully",
            "zip_path": zip_path,
            #"file_count": len(java_files), # Removed.
            #"files": java_files # Removed.
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching repository: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository: {str(e)}")
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
            "branch": "master",  # Default to master, could be main too
            "token": None  # Or fetch this from somewhere if needed
        }
        
        fetch_result = await fetch_repo(repo_details)
        zip_path = fetch_result.get("zip_path")
        
        # Get the file listing for Java files in the ZIP
        with open(zip_path, 'rb') as f:
            files = {'folder': (os.path.basename(zip_path), f, 'application/zip')}
            #updating the code to point to the service itself
            response = requests.post("http://localhost:8001/upload-folder", files=files)
            #response = requests.post("http://fan-in-service:8001/upload-folder", files=files)
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
#removing fetch to directly download zip
#async def fetch_java_files( #REMOVE
#     owner: str, #REMOVE
#     repo: str, #REMOVE
#     branch: str, #REMOVE
#     token: Optional[str], #REMOVE
#     path: str, #REMOVE
#     output_dir: str #REMOVE
# ) -> List[str]:#REMOVE
#     java_files = []#REMOVE
#     headers = {"Accept": "application/vnd.github.v3+json"}#REMOVE
#     if token:#REMOVE
#         headers["Authorization"] = f"token {token}"#REMOVE
#     url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/{path}"#REMOVE
#     if branch:#REMOVE
#         url += f"?ref={branch}"#REMOVE
#     logger.info(f"Fetching repository contents from: {url}")#REMOVE
#     response = requests.get(url, headers=headers)#REMOVE
#     if response.status_code != 200:#REMOVE
#         logger.error(f"Failed to fetch repository contents: {response.status_code} - {response.text}")#REMOVE
#         raise HTTPException(#REMOVE
#             status_code=response.status_code,#REMOVE
#             detail=f"GitHub API error: {response.json().get('message', 'Unknown error')}"#REMOVE
#         )#REMOVE
#     contents = response.json()#REMOVE
#     if not isinstance(contents, list):#REMOVE
#         contents = [contents]#REMOVE
#     for item in contents:#REMOVE
#         item_path = item.get("path")#REMOVE
#         item_type = item.get("type")#REMOVE
#         if item_type == "dir":#REMOVE
#             nested_path = item.get("path", "")#REMOVE
#             nested_files = await fetch_java_files(#REMOVE
#                 owner=owner,#REMOVE
#                 repo=repo,#REMOVE
#                 branch=branch,#REMOVE
#                 token=token,#REMOVE
#                 path=nested_path,#REMOVE
#                 output_dir=output_dir#REMOVE
#             )#REMOVE
#             java_files.extend(nested_files)#REMOVE
#         elif item_type == "file" and item_path.endswith(".java"):#REMOVE
#             download_url = item.get("download_url")#REMOVE
#             if not download_url:#REMOVE
#                 content_base64 = item.get("content", "")#REMOVE
#                 content = base64.b64decode(content_base64).decode("utf-8")#REMOVE
#             else:#REMOVE
#                 file_response = requests.get(download_url, headers=headers)#REMOVE
#                 if file_response.status_code != 200:#REMOVE
#                     logger.warning(f"Failed to download file {item_path}: {file_response.status_code}")#REMOVE
#                     continue#REMOVE
#                 content = file_response.text#REMOVE
#             rel_path = item_path#REMOVE
#             file_path = os.path.join(output_dir, rel_path)#REMOVE
#             os.makedirs(os.path.dirname(file_path), exist_ok=True)#REMOVE
#             with open(file_path, "w", encoding="utf-8") as f:#REMOVE
#                 f.write(content)#REMOVE
#             java_files.append(file_path)#REMOVE
#     return java_files#REMOVE

@app.get("/download")
async def download_zip(path: str = Query(..., description="Path to the ZIP file")):
    if not os.path.exists(path):
        return {"error": "ZIP file not found"}

    return FileResponse(path, filename=os.path.basename(path), media_type="application/zip")
#async def call_fan_in_service(zip_path: str, function_name: str):

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
        # Extract parameters from repo_details
        owner = repo_details.get("owner")
        repo = repo_details.get("repo")
        branch = repo_details.get("branch")
        token = repo_details.get("token")
        function_name = repo_details.get("function_name")  # Function name needed for fan-in/out
        
        # Validate required parameters
        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Repository owner and name are required")
        if not function_name:
            raise HTTPException(status_code=400, detail="Function name is required for analysis")
        
        # Download the zip file
        try:
            zip_path = download_github_zip(owner, repo, branch, token)
        except HTTPException as e:
            raise e
        
        logger.info(f"ZIP file downloaded to: {zip_path}")
        
        # Call the file listing service to get the Java files
        try:
            with open(zip_path, 'rb') as f:
                files = {'folder': (os.path.basename(zip_path), f, 'application/zip')}
                response = requests.post("http://localhost:8001/upload-folder", files=files)
                response.raise_for_status()
                file_list_result = response.json()
                java_files = file_list_result.get("files", [])
            logger.info(f"File listing service returned {len(java_files)} files")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling file listing service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get file list: {str(e)}")
        
        # Call the fan-in and fan-out services
        fan_in_result = await call_fan_in_service(zip_path, function_name)
        fan_out_result = await call_fan_out_service(zip_path, function_name)
        
        # Return the results
        return {
            "status": "success",
            "message": "Repository analyzed successfully",
            "zip_path": zip_path,
            "java_files": java_files,
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
            "branch": "master",  # Default to master, could be main too
            "token": None  # Or fetch this from somewhere if needed
        }
        
        fetch_result = await fetch_repo(repo_details)
        zip_path = fetch_result.get("zip_path")
        
        # Get the file listing for Java files in the ZIP
        with open(zip_path, 'rb') as f:
            files = {'folder': (os.path.basename(zip_path), f, 'application/zip')}
            #updating the code to point to the service itself
            response = requests.post("http://localhost:8001/upload-folder", files=files)
            #response = requests.post("http://fan-in-service:8001/upload-folder", files=files)
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
@app.get("/download")
async def download_zip(path: str = Query(..., description="Path to the ZIP file")):
    if not os.path.exists(path):
        return {"error": "ZIP file not found"}

    return FileResponse(path, filename=os.path.basename(path), media_type="application/zip")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
