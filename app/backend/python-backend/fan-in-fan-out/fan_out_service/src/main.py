from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fetch_repo import fetch_repo
import os
import logging
import traceback
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from fetch_repo import fetch_repo

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fan-out-service")

app = FastAPI(
    title="Fan-out Metrics Service",
    description="Service for calculating Fan-out metrics for all classes in a repository",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODELS ==========

class RepoURLRequest(BaseModel):
    repo_url: str

class ClassScore(BaseModel):
    class_name: str
    score: int

class MetricsResponse(BaseModel):
    timestamp: str
    data: List[ClassScore]

# ========== JAVA PARSER INITIALIZATION ==========

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
                import urllib.request
                logger.info("Downloading JavaParser JAR...")
                urllib.request.urlretrieve(
                    "https://repo1.maven.org/maven2/com/github/javaparser/javaparser-core/3.24.4/javaparser-core-3.24.4.jar",
                    jar_path
                )
                logger.info("Downloaded JavaParser JAR.")

            jpype.startJVM(classpath=[jar_path])
            logger.info("JVM started.")

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
                try:
                    compilation_unit = self.StaticJavaParser.parse(source_code)
                    from java.util import HashSet
                    target_method_node = None
                    for node in compilation_unit.findAll(MethodDeclaration):
                        if node.getNameAsString() == target_method:
                            target_method_node = node
                            break

                    if target_method_node is None:
                        return 0

                    called_methods = HashSet()
                    method_body = target_method_node.getBody()
                    if method_body.isPresent():
                        for call_node in method_body.get().findAll(MethodCallExpr):
                            called_methods.add(call_node.getNameAsString())

                    python_called_methods = set(str(m) for m in called_methods)
                    python_called_methods.discard(target_method)
                    return len(python_called_methods)

                except Exception as e:
                    logger.error(f"JavaParser error for {target_method}: {str(e)}")
                    return 0

        global analyzer
        analyzer = JavaParserFanOutAnalyzer()
        logger.info("JavaParser analyzer initialized.")

    except Exception as e:
        logger.error(f"Error initializing JavaParser: {str(e)}")
        logger.error(traceback.format_exc())

# ========== HELPERS ==========

def get_analyzer():
    if 'analyzer' in globals():
        return analyzer
    raise HTTPException(status_code=500, detail="Analyzer not initialized")

def get_current_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ========== MAIN FAN-OUT ENDPOINT ==========

@app.post("/fan-out")
async def calculate_fan_out_from_repo(
    repo_url_request: RepoURLRequest,
    analyzer: Optional[Any] = Depends(get_analyzer)
):
    try:
        logger.info(f"Received fan-out request for repo: {repo_url_request.repo_url}")
        repo_url = repo_url_request.repo_url
        sha, repo_path = fetch_repo(repo_url)

        java_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".java"):
                    java_files.append(os.path.join(root, file))

        logger.info(f"Found {len(java_files)} Java files.")

        class_metrics: Dict[str, int] = {}

        for file_path in java_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try parsing file
                try:
                    from com.github.javaparser.ast.body import MethodDeclaration
                    compilation_unit = StaticJavaParser.parse(content)
                    method_decls = compilation_unit.findAll(MethodDeclaration)
                except Exception as e:
                    logger.warning(f"Skipping file due to parse error (record?): {file_path}")
                    logger.warning(str(e))
                    continue

                class_name = str(analyzer.extract_class_name(content))
                total_fan_out = 0

                for method in method_decls:
                    method_name = method.getNameAsString()
                    try:
                        fan_out = analyzer.analyze_fan_out(content, method_name)
                        total_fan_out += fan_out
                    except Exception as e:
                        logger.warning(f"Error analyzing {method_name} in {file_path}: {str(e)}")
                        continue

                class_metrics[class_name] = total_fan_out

            except Exception as e:
                logger.warning(f"Failed to process file {file_path}: {str(e)}")
                continue

        data = [ClassScore(class_name=str(k), score=v) for k, v in class_metrics.items()]
        return MetricsResponse(timestamp=get_current_timestamp(), data=data).dict()

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")
    except Exception as e:
        logger.error(f"Error during fan-out analysis: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ========== HEALTH & ROOT ==========

@app.get("/")
async def root():
    return {"message": "Fan-out Metrics Service for Java Classes"}

@app.get("/health")
async def health_check():
    jvm_status = "initialized" if 'jpype' in globals() and jpype.isJVMStarted() else "not initialized"
    return {"status": "healthy", "javaparser": jvm_status}

# ========== RUN LOCALLY ==========
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Fan-out Metrics Service on 0.0.0.0:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
