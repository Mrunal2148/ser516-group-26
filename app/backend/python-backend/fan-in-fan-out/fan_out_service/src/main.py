from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import zipfile
import tempfile
import os
import shutil
import json
from typing import List, Dict, Any, Optional, Set
import logging
import traceback
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fan-out-service")

app = FastAPI(
    title="Fan-out Metrics Service",
    description="Service for calculating Fan-out metrics using JavaParser",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
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

#classes for new resposnse   
class ClassScore(BaseModel):
    class_name: str
    score: int

class MetricsResponse(BaseModel):
    timestamp: str
    data: List[ClassScore]
    
@app.on_event("startup")
async def initialize_javaparser():
    try:
        global jpype, StaticJavaParser, JavaParserFanOutAnalyzer
        
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
        from com.github.javaparser.ast.expr import MethodCallExpr
        from com.github.javaparser.ast.body import MethodDeclaration
        
        class JavaParserFanOutAnalyzer:
            def __init__(self):
                self.StaticJavaParser = StaticJavaParser
                self.VoidVisitorAdapter = VoidVisitorAdapter
            
            def extract_class_name(self, source_code: str) -> str:
            
                try:
                    compilation_unit = self.StaticJavaParser.parse(source_code)
                    
                    package_name = ""
                    if compilation_unit.getPackageDeclaration().isPresent():
                        package_name = compilation_unit.getPackageDeclaration().get().getNameAsString()
                    
                    class_name = ""
                    if compilation_unit.getPrimaryType().isPresent():
                        class_name = compilation_unit.getPrimaryType().get().getNameAsString()
                    else:
                        types = compilation_unit.getTypes()
                        if types.size() > 0:
                            class_name = types.get(0).getNameAsString()
                    
                    if package_name and class_name:
                        return f"{package_name}.{class_name}"
                    return class_name
                except Exception as e:
                    logger.error(f"Error extracting class name: {str(e)}")
                    return "unknown.Class"
            
            def analyze_fan_out(self, source_code: str, target_method: str) -> int:
                """
                Use JavaParser to accurately calculate fan-out for a target method
                
                Args:
                    source_code: Java source code
                    target_method: Target method name to analyze
                    
                Returns:
                    Number of other methods called by the target method
                """
                try:
                    # Parse Java code
                    compilation_unit = self.StaticJavaParser.parse(source_code)
                    
                    # Import necessary Java classes
                    from com.github.javaparser.ast.body import MethodDeclaration
                    from com.github.javaparser.ast.expr import MethodCallExpr
                    from java.util import HashSet
                    
                    # Find the target method directly - no need for visitors
                    target_method_node = None
                    
                    # Find all method declarations with the target name
                    for node in compilation_unit.findAll(MethodDeclaration):
                        if node.getNameAsString() == target_method:
                            target_method_node = node
                            break
                    
                    # If method not found, return 0
                    if target_method_node is None:
                        return 0
                    
                    # Create a set to store called methods
                    called_methods = HashSet()
                    
                    # Get the method body
                    method_body = target_method_node.getBody()
                    if method_body.isPresent():
                        # Find all method calls within the method body
                        for call_node in method_body.get().findAll(MethodCallExpr):
                            # Add method name to our set
                            called_methods.add(call_node.getNameAsString())
                    
                    # Convert Java Set to Python set
                    python_called_methods = set([method_name for method_name in called_methods])
                    
                    # Remove recursive calls to the target method itself
                    if target_method in python_called_methods:
                        python_called_methods.remove(target_method)
                    
                    return len(python_called_methods)
                    
                except Exception as e:
                    logger.error(f"Error analyzing with JavaParser: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Fall back to regex in case of JavaParser error
                    return self._fallback_regex_analysis(source_code, target_method)
            
            def _fallback_regex_analysis(self, source_code: str, target_method: str) -> int:
                """Fallback to regex-based analysis if JavaParser fails"""
                import re
                
                method_pattern = re.compile(
                    r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(' + 
                    re.escape(target_method) + 
                    r')\s*\([^\)]*\)\s*\{((?:[^{}]|(?:\{[^{}]*\}))*)\}'
                )
                method_match = method_pattern.search(source_code)
                
                if not method_match:
                    return 0
                    
                method_body = method_match.group(2)
                
                call_pattern = re.compile(r'(?<!\w)(\w+)(?:\s*\([^\)]*\))')
                method_calls = call_pattern.findall(method_body)
                
                unique_calls = set(method_calls)
                if target_method in unique_calls:
                    unique_calls.remove(target_method)
                    
                return len(unique_calls)
        
        global analyzer
        analyzer = JavaParserFanOutAnalyzer()
        logger.info("JavaParser analyzer initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing JavaParser: {str(e)}")
        logger.error(traceback.format_exc())

def get_analyzer():
    """Dependency injection for the analyzer"""
    if 'analyzer' in globals():
        return globals()['analyzer']
    return None

def get_current_timestamp():
   
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def extract_class_name_regex(source_code: str) -> str:
    
    import re
    
    package_match = re.search(r'package\s+([a-zA-Z0-9_.]+);', source_code)
    package_name = package_match.group(1) if package_match else ""
    
    class_match = re.search(r'(?:public|private|protected)?\s+class\s+([a-zA-Z0-9_]+)', source_code)
    class_name = class_match.group(1) if class_match else "UnknownClass"
    
    if package_name:
        return f"{package_name}.{class_name}"
    return class_name

def fan_out_metric(source_code: str, target: str, analyzer=None) -> (int, str):
   
    try:
        class_name = "unknown.Class"
        if analyzer:
            class_name = analyzer.extract_class_name(source_code)
            fan_out = analyzer.analyze_fan_out(source_code, target)
            return fan_out, class_name
        
        class_name = extract_class_name_regex(source_code)
        
        import re
        
        method_pattern = re.compile(
            r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(' + 
            re.escape(target) + 
            r')\s*\([^\)]*\)\s*\{((?:[^{}]|(?:\{[^{}]*\}))*)\}'
        )
        method_match = method_pattern.search(source_code)
        
        if not method_match:
            return 0, class_name
            
        method_body = method_match.group(2)
        
        call_pattern = re.compile(r'(?<!\w)(\w+)(?:\s*\([^\)]*\))')
        method_calls = call_pattern.findall(method_body)
        
        unique_calls = set(method_calls)
        if target in unique_calls:
            unique_calls.remove(target)
            
        return len(unique_calls), class_name
        
    except Exception as e:
        logger.error(f"Error in fan_out_metric: {str(e)}")
        logger.error(traceback.format_exc())
        return 0, "unknown.Class"

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

@app.post("/metrics/fan-out-scoped")
async def calculate_scoped_fan_out(
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
            
            data = []
            
            for file_path in scope_request.selected_files:
                full_path = os.path.join(temp_dir, file_path)
                
                if os.path.exists(full_path) and file_path.endswith('.java'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_fan_out, class_name = fan_out_metric(content, scope_request.function_name, analyzer)
                        data.append(ClassScore(
                            class_name=class_name, 
                            score=file_fan_out
                        ))
                else:
                    logger.warning(f"File not found or not a Java file: {file_path}")
            
            return MetricsResponse(
                timestamp=get_current_timestamp(),
                data=data
            ).dict()
            
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error in calculate_scoped_fan_out: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

@app.post("/metrics/fan-out-multi")
async def calculate_multi_fan_out(
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
        
        class_name = "unknown.Class"
        if analyzer:
            class_name = analyzer.extract_class_name(source_code)
        else:
            class_name = extract_class_name_regex(source_code)
        
        data = []
        for function_name in function_names_list:
            fan_out, _ = fan_out_metric(source_code, function_name, analyzer)
            data.append(ClassScore(
                class_name=f"{class_name}#{function_name}", 
                score=fan_out
            ))
        
        return MetricsResponse(
            timestamp=get_current_timestamp(),
            data=data
        ).dict()
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for function_names")
    except Exception as e:
        logger.error(f"Error in calculate_multi_fan_out: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/metrics/fan-out-scoped-multi")
async def calculate_scoped_multi_fan_out(
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
            
            data = []
            
            for file_path in scope_request.selected_files:
                full_path = os.path.join(temp_dir, file_path)
                
                if os.path.exists(full_path) and file_path.endswith('.java'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        class_name = "unknown.Class"
                        if analyzer:
                            class_name = analyzer.extract_class_name(content)
                        else:
                            class_name = extract_class_name_regex(content)
                        
                        for function_name in scope_request.function_names:
                            file_fan_out, _ = fan_out_metric(content, function_name, analyzer)
                            data.append(ClassScore(
                                class_name=f"{class_name}#{function_name}", 
                                score=file_fan_out
                            ))
                else:
                    logger.warning(f"File not found or not a Java file: {file_path}")
            
            return MetricsResponse(
                timestamp=get_current_timestamp(),
                data=data
            ).dict()
            
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            logger.error(f"Error in calculate_scoped_multi_fan_out: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Fan-out Metrics Service with JavaParser Integration"}

@app.get("/health")
async def health_check():
    jvm_status = "initialized" if 'jpype' in globals() and jpype.isJVMStarted() else "not initialized"
    return {
        "status": "healthy",
        "javaparser": jvm_status
    }

@app.post("/metrics/fan-out")
async def calculate_fan_out(
    file: UploadFile = File(...), 
    function_name: str = Form(...),
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    if not file.filename.endswith('.java'):
        raise HTTPException(status_code=400, detail="Only Java files are supported")
    
    try:
        content = await file.read()
        source_code = content.decode('utf-8')
        
        fan_out, class_name = fan_out_metric(source_code, function_name, analyzer)
        
        return MetricsResponse(
            timestamp=get_current_timestamp(),
            data=[
                ClassScore(
                    class_name=class_name,
                    score=fan_out
                )
            ]
        ).dict()
    except Exception as e:
        logger.error(f"Error in calculate_fan_out: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)