from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import zipfile
import tempfile
import os
import shutil
import json
from typing import List, Dict, Any, Optional
import logging
import traceback
from datetime import datetime

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fan-in-service")

class FileInfo(BaseModel):
    path: str
    name: str

class ScopeRequest(BaseModel):
    selected_files: List[str]
    function_name: str

class MultiFunctionScopeRequest(BaseModel):
    selected_files: List[str]
    function_names: List[str]

def extract_class_name(file_path: str) -> str:
    return (
        file_path.replace("/", ".")
                 .replace("\\", ".")
                 .replace(".java", "")
                 .strip(".")
    )

def format_final_response(entries: List[dict]) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": entries
    }

@asynccontextmanager
async def lifespan(app):
    print("FastAPI lifespan startup triggered")
    try:
        global jpype, StaticJavaParser, JavaParserFanInAnalyzer

        import jpype
        import jpype.imports

        libs_dir = os.path.join(os.path.dirname(__file__), "libs")
        os.makedirs(libs_dir, exist_ok=True)

        jar_path = os.path.join(libs_dir, "javaparser-core-3.24.4.jar")
        if not os.path.exists(jar_path):
            print("⚠️ Downloading JavaParser JAR...")
            import urllib.request
            urllib.request.urlretrieve(
                "https://repo1.maven.org/maven2/com/github/javaparser/javaparser-core/3.24.4/javaparser-core-3.24.4.jar",
                jar_path
            )
            print("✅ Downloaded")

        if not jpype.isJVMStarted():
            print("🚀 Starting JVM...")
            jpype.startJVM(classpath=[jar_path])
            print("✅ JVM started")

        from com.github.javaparser import StaticJavaParser
        from com.github.javaparser.ast.visitor import VoidVisitorAdapter

        class JavaParserFanInAnalyzer:
            def __init__(self):
                self.StaticJavaParser = StaticJavaParser
                self.VoidVisitorAdapter = VoidVisitorAdapter

            def analyze_fan_in(self, source_code: str, target_method: str) -> int:
                print(f"🔍 Analyzing method: {target_method}")
                compilation_unit = self.StaticJavaParser.parse(source_code)
                print("✅ Parsed source code")
                # Import MethodCallExpr directly via jpype
                MethodCallExpr = jpype.JClass("com.github.javaparser.ast.expr.MethodCallExpr")
                print("✅ Loaded MethodCallExpr class")
                count = 0
                # Use Java streams to filter all method calls
                method_calls = compilation_unit.findAll(MethodCallExpr)
                print(f"🔍 Found {len(method_calls)} method calls")
                for mc in method_calls:
                    method_name = mc.getNameAsString()
                    print(f"➡️ Method call: {method_name}")
                    if method_name == target_method:
                        count += 1
                print(f"✅ Total fan-in for {target_method}: {count}")
                return count
        
        global analyzer  # 👈 make it available to get_analyzer()
        analyzer = JavaParserFanInAnalyzer()
        print("✅ JavaParserFanInAnalyzer instance created")

    except Exception as e:
        import traceback
        print("🔥 JVM initialization failed!")
        print(e)
        print(traceback.format_exc())

    yield  # <-- this is what lets FastAPI finish startup

def get_analyzer():
    """Dependency injection for the analyzer"""
    if 'analyzer' in globals():
        return globals()['analyzer']
    raise HTTPException(
        status_code=500, 
        detail="JavaParser analyzer not initialized. Please try again later."
    )

app = FastAPI(
    title="Fan-in Metrics Service",
    description="Service for calculating Fan-in metrics using JavaParser",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fan_in_metric(source_code: str, target: str, analyzer=None) -> int:
   
    try:
        if analyzer:
            return analyzer.analyze_fan_in(source_code, target)
        
        import re
        
        method_def_pattern = re.compile(
            r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+' + 
            re.escape(target) + 
            r'\s*\([^\)]*\)\s*(?:\{|throws)'
        )
        
        call_pattern = re.compile(
            r'(?<!new\s)(?<!\w)(?<!@)(\w+\.)?' + re.escape(target) + r'\s*\('
        )
        
        method_defs = method_def_pattern.finditer(source_code)
        exclude_positions = [(m.start(), m.end()) for m in method_defs]
        
        calls = call_pattern.finditer(source_code)
        count = 0
        
        for call in calls:
            is_excluded = False
            for start, end in exclude_positions:
                if start <= call.start() <= end:
                    is_excluded = True
                    break
            
            if not is_excluded:
                count += 1
        
        return count
        
    except Exception as e:
        logger.error(f"Error in fan_in_metric: {str(e)}")
        logger.error(traceback.format_exc())
        import re
        pattern = re.compile(r'(?<!new\s)(?<!\w)(?<!@)(\w+\.)?' + re.escape(target) + r'\s*\(')
        # return len(pattern.findall(source_code))
        print(len(pattern.findall(source_code)))
        import traceback
        print("🔥 ERROR IN fan_in_metric 🔥")
        print(e)
        print(traceback.format_exc())
        raise

@app.post("/upload-folder")
async def upload_folder(folder: UploadFile = File(...)):
    if not folder.filename.endswith(('.zip', '.ZIP')):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, folder.filename)
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(folder.file, buffer)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            java_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.java'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, temp_dir)
                        java_files.append(FileInfo(
                            path=rel_path,
                            name=os.path.basename(file)
                        ))
            
            return {"files": java_files}
        
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error in upload_folder: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing folder: {str(e)}"
            )

@app.post("/metrics/fan-in-scoped")
async def calculate_scoped_fan_in(
    folder: UploadFile = File(...),
    scope: str = Form(...),
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    try:
        scope_data = json.loads(scope)
        scope_request = ScopeRequest(**scope_data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scope format: {str(e)}"
        )

    if not folder.filename.endswith(('.zip', '.ZIP')):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, folder.filename)
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(folder.file, buffer)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            results = {}
            total_fan_in = 0
            
            for file_path in scope_request.selected_files:
                full_path = os.path.join(temp_dir, file_path)
                
                if os.path.exists(full_path) and file_path.endswith('.java'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_fan_in = fan_in_metric(content, scope_request.function_name, analyzer)
                        results[file_path] = file_fan_in
                        total_fan_in += file_fan_in
                else:
                    results[file_path] = "File not found or not a Java file"
            
            return {
                "function_name": scope_request.function_name,
                "total_fan_in": total_fan_in,
                "per_file_results": results
            }
            
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error in calculate_scoped_fan_in: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

@app.post("/metrics/fan-in-multi")
async def calculate_multi_fan_in(
    file: UploadFile = File(...), 
    function_names: str = Form(...),
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    if not file.filename.endswith('.java'):
        raise HTTPException(status_code=400, detail="Only Java files are supported")
    
    try:
        function_names_list = json.loads(function_names)
        if not isinstance(function_names_list, list):
            raise HTTPException(status_code=400, detail="function_names must be a JSON array")
        
        content = await file.read()
        source_code = content.decode('utf-8')
        class_name = extract_class_name(file.filename)

        results = []
        for function_name in function_names_list:
            fan_in = fan_in_metric(source_code, function_name, analyzer)
            results.append({
                "class_name": class_name,
                "method_name": function_name,
                "fan_in_score": fan_in
            })

        return format_final_response(results)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for function_names")
    except Exception as e:
        logger.error(f"Error in calculate_multi_fan_in: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/metrics/fan-in-scoped-multi")
async def calculate_scoped_multi_fan_in(
    folder: UploadFile = File(...),
    scope: str = Form(...),
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    try:
        scope_data = json.loads(scope)
        if "function_names" not in scope_data:
            if "function_name" in scope_data:
                scope_data["function_names"] = [scope_data["function_name"]]
            else:
                raise HTTPException(status_code=400, detail="Missing function_names in scope")
                
        scope_request = MultiFunctionScopeRequest(**scope_data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scope format: {str(e)}"
        )

    if not folder.filename.endswith(('.zip', '.ZIP')):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, folder.filename)
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(folder.file, buffer)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            final_entries = []

            for function_name in scope_request.function_names:
                for file_path in scope_request.selected_files:
                    full_path = os.path.join(temp_dir, file_path)
                    
                    if os.path.exists(full_path) and file_path.endswith('.java'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_fan_in = fan_in_metric(content, function_name, analyzer)

                            final_entries.append({
                                "class_name": extract_class_name(file_path),
                                "method_name": function_name,
                                "fan_in_score": file_fan_in
                            })
                    else:
                        logger.warning(f"Skipping invalid file: {file_path}")
                        continue

            return format_final_response(final_entries)
        
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error in calculate_scoped_multi_fan_in: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Fan-in Metrics Service with JavaParser Integration"}

@app.get("/health")
async def health_check():
    jvm_status = "initialized" if 'jpype' in globals() and jpype.isJVMStarted() else "not initialized"
    return {
        "status": "healthy",
        "javaparser": jvm_status
    }

@app.post("/metrics/fan-in")
async def calculate_fan_in(
    file: UploadFile = File(...), 
    function_name: str = Form(...),
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    if not file.filename.endswith('.java'):
        raise HTTPException(status_code=400, detail="Only Java files are supported")
    
    try:
        content = await file.read()
        source_code = content.decode('utf-8')

        fan_in = fan_in_metric(source_code, function_name, analyzer)

        # Extract class name from uploaded file
        class_name = extract_class_name(file.filename)

        response = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": [
                {
                    "class_name": class_name,
                    "method_name": function_name,
                    "fan_in_score": fan_in
                }
            ]
        }
        return response

    except Exception as e:
        logger.error(f"Error in calculate_fan_in: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)