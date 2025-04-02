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

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fan-in-service")

app = FastAPI(
    title="Fan-in Metrics Service",
    description="Service for calculating Fan-in metrics using JavaParser",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileInfo(BaseModel):
    path: str
    name: str

class ScopeRequest(BaseModel):
    selected_files: List[str]
    function_name: str

class MultiFunctionScopeRequest(BaseModel):
    selected_files: List[str]
    function_names: List[str]
    
@app.on_event("startup")
async def initialize_javaparser():
    try:
        global jpype, StaticJavaParser, JavaParserFanInAnalyzer
        
        import jpype
        import jpype.imports
        
        if not jpype.isJVMStarted():
            libs_dir = os.path.join(os.path.dirname(__file__), "libs")
            os.makedirs(libs_dir, exist_ok=True)
            
            jar_path = os.path.join(libs_dir, "javaparser-core-3.24.4.jar")
            if not os.path.exists(jar_path):
                logger.info("JavaParser JAR not found. Downloading...")
                import urllib.request
                urllib.request.urlretrieve(
                    "https://repo1.maven.org/maven2/com/github/javaparser/javaparser-core/3.24.4/javaparser-core-3.24.4.jar",
                    jar_path
                )
                logger.info("JavaParser JAR downloaded successfully")
            
            logger.info("Starting JVM with JavaParser...")
            jpype.startJVM(classpath=[jar_path])
            logger.info("JVM started successfully")
        
        from com.github.javaparser import StaticJavaParser
        from com.github.javaparser.ast.visitor import VoidVisitorAdapter
        
        class JavaParserFanInAnalyzer:
            def __init__(self):
                self.StaticJavaParser = StaticJavaParser
                self.VoidVisitorAdapter = VoidVisitorAdapter
            
            def analyze_fan_in(self, source_code: str, target_method: str) -> int:
                try:
                    compilation_unit = self.StaticJavaParser.parse(source_code)
                    
                    from com.github.javaparser.ast.expr import MethodCallExpr
                    from com.github.javaparser.ast.body import MethodDeclaration
                    
                    method_calls = []
                    method_definitions = []
                    
                    for node in compilation_unit.findAll(MethodCallExpr):
                        if node.getNameAsString() == target_method:
                            method_calls.append(node)
                    
                    for node in compilation_unit.findAll(MethodDeclaration):
                        if node.getNameAsString() == target_method:
                            method_definitions.append(node)
                    
                    valid_calls = []
                    for call in method_calls:
                        is_in_definition = False
                        for definition in method_definitions:
                            if (call.getBegin().isPresent() and 
                                definition.getBegin().isPresent() and
                                definition.getEnd().isPresent() and
                                call.getBegin().get().line >= definition.getBegin().get().line and
                                call.getBegin().get().line <= definition.getEnd().get().line):
                                is_in_definition = True
                                break
                        
                        if not is_in_definition:
                            valid_calls.append(call)
                    
                    return len(valid_calls)
                    
                except Exception as e:
                    logger.error(f"Error analyzing with JavaParser: {str(e)}")
                    logger.error(traceback.format_exc())
                    return self._fallback_regex_analysis(source_code, target_method)
            
            def _fallback_regex_analysis(self, source_code: str, target_method: str) -> int:
                """Fallback to regex-based analysis if JavaParser fails"""
                import re
                
                method_def_pattern = re.compile(
                    r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+' + 
                    re.escape(target_method) + 
                    r'\s*\([^\)]*\)\s*(?:\{|throws)'
                )
                
                call_pattern = re.compile(
                    r'(?<!new\s)(?<!\w)(?<!@)(\w+\.)?' + 
                    re.escape(target_method) + 
                    r'\s*\('
                )
                
                method_defs = list(method_def_pattern.finditer(source_code))
                exclude_positions = [(m.start(), m.end()) for m in method_defs]
                
                calls = list(call_pattern.finditer(source_code))
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
        
        global analyzer
        analyzer = JavaParserFanInAnalyzer()
        logger.info("JavaParser analyzer initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing JavaParser: {str(e)}")
        logger.error(traceback.format_exc())

def get_analyzer():
    """Dependency injection for the analyzer"""
    if 'analyzer' in globals():
        return globals()['analyzer']
    raise HTTPException(
        status_code=500, 
        detail="JavaParser analyzer not initialized. Please try again later."
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
        return len(pattern.findall(source_code))

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
        
        results = {}
        for function_name in function_names_list:
            fan_in = fan_in_metric(source_code, function_name, analyzer)
            results[function_name] = fan_in
        
        return {
            "results": results
        }
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
            
            all_results = {}
            
            for function_name in scope_request.function_names:
                results = {}
                total_fan_in = 0
                
                for file_path in scope_request.selected_files:
                    full_path = os.path.join(temp_dir, file_path)
                    
                    if os.path.exists(full_path) and file_path.endswith('.java'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_fan_in = fan_in_metric(content, function_name, analyzer)
                            results[file_path] = file_fan_in
                            total_fan_in += file_fan_in
                    else:
                        results[file_path] = "File not found or not a Java file"
                
                all_results[function_name] = {
                    "total_fan_in": total_fan_in,
                    "per_file_results": results
                }
            
            return {
                "results": all_results
            }
            
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
        
        return {
            "function_name": function_name,
            "fan_in": fan_in
        }
    except Exception as e:
        logger.error(f"Error in calculate_fan_in: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)