from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from response_wrapper import wrap_with_timestamp
from fetch_repo import fetch_repo
import os
import logging
import traceback
from datetime import datetime
from typing import List, Any, Optional, Dict
import re

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fan-in-service")

app = FastAPI(
    title="Fan-in Metrics Service",
    description="Service for calculating Fan-in metrics for all classes in a repository",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoURLRequest(BaseModel):
    repo_url: str

@app.on_event("startup")
async def initialize_javaparser():
    try:
        global jpype, StaticJavaParser, JavaParserAnalyzer
        
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
        
        class JavaParserAnalyzer:
            def __init__(self):
                self.StaticJavaParser = StaticJavaParser
                self.VoidVisitorAdapter = VoidVisitorAdapter
            
            def analyze_fan_in(self, source_code: str) -> Dict[str, int]:
                """Analyze the fan-in for all methods in the source code"""
                try:
                    compilation_unit = self.StaticJavaParser.parse(source_code)
                    
                    from com.github.javaparser.ast.expr import MethodCallExpr
                    from com.github.javaparser.ast.body import MethodDeclaration
                    
                    # Get all method declarations and method calls
                    method_declarations = compilation_unit.findAll(MethodDeclaration)
                    method_calls = compilation_unit.findAll(MethodCallExpr)
                    
                    # Map to store method names and their fan-in scores
                    method_fan_in = {}
                    
                    # Process all method declarations
                    for declaration in method_declarations:
                        method_name = declaration.getNameAsString()
                        if method_name not in method_fan_in:
                            method_fan_in[method_name] = 0
                    
                    # Process all method calls
                    for call in method_calls:
                        called_method = call.getNameAsString()
                        if called_method in method_fan_in:
                            method_fan_in[called_method] += 1
                    
                    return method_fan_in
                    
                except Exception as e:
                    logger.error(f"Error analyzing with JavaParser: {str(e)}")
                    logger.error(traceback.format_exc())
                    return self._fallback_regex_analysis(source_code)
            
            def _fallback_regex_analysis(self, source_code: str) -> Dict[str, int]:
                """Fallback regex analysis for all methods"""
                try:
                    import re
                    
                    # Find all method declarations
                    method_def_pattern = re.compile(
                        r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*(?:\{|throws)'
                    )
                    
                    # Extract method names from declarations
                    method_names = [m.group(1) for m in method_def_pattern.finditer(source_code)]
                    
                    # Initialize fan-in counts for all methods
                    method_fan_in = {name: 0 for name in method_names}
                    
                    # Count method calls for each method
                    for method_name in method_names:
                        # Find all calls to this method
                        call_pattern = re.compile(
                            r'(?<!new\s)(?<!\w)(?<!@)(\w+\.)?' + re.escape(method_name) + r'\s*\('
                        )
                        
                        # Count calls excluding those within the method's own definition
                        calls = list(call_pattern.finditer(source_code))
                        count = 0
                        
                        # Extract positions of all method definitions to exclude self-calls
                        method_defs = list(method_def_pattern.finditer(source_code))
                        exclude_positions = []
                        
                        for m in method_defs:
                            if m.group(1) == method_name:
                                # Find the method body boundaries
                                start_pos = m.start()
                                
                                # Simple approach to find matching brace - can be improved
                                open_braces = 0
                                end_pos = m.end()
                                
                                for i in range(m.end(), len(source_code)):
                                    if source_code[i] == '{':
                                        open_braces += 1
                                    elif source_code[i] == '}':
                                        open_braces -= 1
                                        if open_braces <= 0:
                                            end_pos = i + 1
                                            break
                                
                                exclude_positions.append((start_pos, end_pos))
                        
                        # Count calls outside method definitions
                        for call in calls:
                            is_excluded = False
                            for start, end in exclude_positions:
                                if start <= call.start() <= end:
                                    is_excluded = True
                                    break
                            
                            if not is_excluded:
                                count += 1
                        
                        method_fan_in[method_name] = count
                    
                    return method_fan_in
                except Exception as e:
                    logger.error(f"Error in fallback analysis: {str(e)}")
                    logger.error(traceback.format_exc())
                    return {}
        
        global analyzer
        analyzer = JavaParserAnalyzer()
        logger.info("JavaParser analyzer initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing JavaParser: {str(e)}")
        logger.error(traceback.format_exc())

def extract_class_name(file_path: str) -> str:
    return (
        file_path.replace("/", ".")
                 .replace("\\", ".")
                 .replace(".java", "")
                 .strip(".")
    )

def format_final_response(class_metrics: Dict[str, int]) -> dict:
    formatted_entries = []
    for class_name, score in class_metrics.items():
        formatted_entries.append({
            "class_name": class_name,
            "score": score
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "data": formatted_entries
    }

def get_analyzer():
    """Dependency injection for the analyzer"""
    if 'analyzer' in globals():
        return globals()['analyzer']
    raise HTTPException(
        status_code=500, 
        detail="JavaParser analyzer not initialized. Please try again later."
    )

def calculate_class_fan_in(java_files: List[str]) -> Dict[str, int]:
    """
    Calculate fan-in metrics for all classes in the provided Java files.
    Returns a dictionary mapping class names to their fan-in scores.
    """
    class_metrics = {}
    
    # Extract all class names first
    for file_path in java_files:
        try:
            class_name = extract_class_name(file_path)
            class_metrics[class_name] = 0
        except Exception as e:
            logger.warning(f"Error processing class name for {file_path}: {str(e)}")
    
    # Calculate fan-in for each class
    for file_path in java_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for imports/references to each class
            for target_class in class_metrics.keys():
                # Count import statements
                import_pattern = re.compile(r'import\s+' + re.escape(target_class) + r'\s*;')
                import_count = len(import_pattern.findall(content))
                
                # Count direct references (simple class name)
                simple_class_name = target_class.split(".")[-1]
                reference_pattern = re.compile(r'\b' + re.escape(simple_class_name) + r'\b')
                reference_count = len(reference_pattern.findall(content))
                
                # Avoid counting self-references in the same class
                if extract_class_name(file_path) == target_class:
                    reference_count = 0
                
                class_metrics[target_class] += import_count + reference_count
        except Exception as e:
            logger.warning(f"Error analyzing file {file_path}: {str(e)}")
    
    return class_metrics

@app.get("/")
async def root():
    return {"message": "Fan-in Metrics Service for Java Classes"}

@app.get("/health")
async def health_check():
    jvm_status = "initialized" if 'jpype' in globals() and jpype.isJVMStarted() else "not initialized"
    return {
        "status": "healthy",
        "javaparser": jvm_status
    }

@app.post("/fan-in")
async def calculate_fan_in_from_repo(repo_url_request: RepoURLRequest, analyzer: Optional[Any] = Depends(get_analyzer)):
    try:
        # Log the request details for debugging
        logger.info(f"Received fan-in request for repo: {repo_url_request.repo_url}")
        logger.info(f"Received fan-in request for repo: {repo_url_request.repo_url}")
        repo_url = repo_url_request.repo_url
        # Using the fetch_repo function from the imported module
        # This assumes the repository has already been cloned by the middleware
        sha, repo_path = fetch_repo(repo_url)
        
        logger.info(f"Successfully fetched repo at: {repo_path} with SHA: {sha}")

        java_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(java_files)} Java files to analyze")

        # Calculate fan-in metrics for all classes
        class_metrics = calculate_class_fan_in(java_files)
        
        logger.info(f"Analysis complete. Found metrics for {len(class_metrics)} classes.")
        return format_final_response(class_metrics)
    
    except FileNotFoundError as e:
        logger.error(f"Repository not found: {str(e)}")
        raise HTTPException(
            status_code=404, 
            detail="Repository not found in shared volume. Please ensure it has been cloned first."
        )
    except Exception as e:
        logger.error(f"Error processing repository: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing repository: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Log startup message with the port and host information
    logger.info("Starting Fan-in Metrics Service on 0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)