from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import asyncio

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api-gateway")

FANIN_URL = "http://fan-in-service:8001" 
FANOUT_URL = "http://fan-out-service:8002" 

app = FastAPI(
    title="Java Fan-in/Fan-out Metrics",
    description="API Gateway for Java Fan-in and Fan-out metrics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to API Gateway"}

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            fanin_response = await client.get(f"{FANIN_URL}/health")
            fanin_status = "healthy" if fanin_response.status_code == 200 else "unhealthy"
            
            fanin_details = {}
            if fanin_response.status_code == 200:
                fanin_json = fanin_response.json()
                if "javaparser" in fanin_json:
                    fanin_details["javaparser"] = fanin_json["javaparser"]
            
            fanout_response = await client.get(f"{FANOUT_URL}/health")
            fanout_status = "healthy" if fanout_response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.error(f"Error checking service health: {str(e)}")
        fanin_status = "unhealthy"
        fanout_status = "unhealthy"
        fanin_details = {"error": str(e)}

    return {
        "status": "healthy",
        "services": {
            "fan_in": {
                "status": fanin_status,
                **fanin_details
            },
            "fan_out": {
                "status": fanout_status
            }
        }
    }

@app.post("/metrics/fan-in")
async def gateway_fan_in(file: UploadFile = File(...), function_name: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, file.file, file.content_type)}
            data = {"function_name": function_name}
            
            logger.info(f"Forwarding fan-in request for file {file.filename}, method {function_name}")
            response = await client.post(
                f"{FANIN_URL}/metrics/fan-in",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Fan-in calculation successful: {result}")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-in service")
                logger.error(f"Fan-in service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-in service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-in service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_in: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-in-scoped")
async def gateway_fan_in_scoped(folder: UploadFile = File(...), scope: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"folder": (folder.filename, folder.file, folder.content_type)}
            data = {"scope": scope}
            
            logger.info(f"Forwarding scoped fan-in request for folder {folder.filename}")
            response = await client.post(
                f"{FANIN_URL}/metrics/fan-in-scoped",
                files=files,
                data=data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Scoped fan-in calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-in service")
                logger.error(f"Fan-in service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-in service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-in service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_in_scoped: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-out")
async def gateway_fan_out(file: UploadFile = File(...), function_name: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, file.file, file.content_type)}
            data = {"function_name": function_name}
            
            logger.info(f"Forwarding fan-out request for file {file.filename}, method {function_name}")
            response = await client.post(
                f"{FANOUT_URL}/metrics/fan-out",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Fan-out calculation successful: {result}")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-out service")
                logger.error(f"Fan-out service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-out service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-out service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_out: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-out-scoped")
async def gateway_fan_out_scoped(folder: UploadFile = File(...), scope: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"folder": (folder.filename, folder.file, folder.content_type)}
            data = {"scope": scope}
            
            logger.info(f"Forwarding scoped fan-out request for folder {folder.filename}")
            response = await client.post(
                f"{FANOUT_URL}/metrics/fan-out-scoped",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Scoped fan-out calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-out service")
                logger.error(f"Fan-out service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-out service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-out service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_out_scoped: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/metrics/fan-in-multi")
async def gateway_multi_fan_in(file: UploadFile = File(...), function_names: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, file.file, file.content_type)}
            data = {"function_names": function_names}
            
            logger.info(f"Forwarding multi-function fan-in request for file {file.filename}")
            response = await client.post(
                f"{FANIN_URL}/metrics/fan-in-multi",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Multi-function fan-in calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-in service")
                logger.error(f"Fan-in service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-in service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-in service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_multi_fan_in: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-out-multi")
async def gateway_multi_fan_out(file: UploadFile = File(...), function_names: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, file.file, file.content_type)}
            data = {"function_names": function_names}
            
            logger.info(f"Forwarding multi-function fan-out request for file {file.filename}")
            response = await client.post(
                f"{FANOUT_URL}/metrics/fan-out-multi",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Multi-function fan-out calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-out service")
                logger.error(f"Fan-out service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-out service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-out service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_multi_fan_out: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-in-scoped-multi")
async def gateway_fan_in_scoped_multi(folder: UploadFile = File(...), scope: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"folder": (folder.filename, folder.file, folder.content_type)}
            data = {"scope": scope}
            
            logger.info(f"Forwarding multi-function scoped fan-in request for folder {folder.filename}")
            response = await client.post(
                f"{FANIN_URL}/metrics/fan-in-scoped-multi",
                files=files,
                data=data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Multi-function scoped fan-in calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-in service")
                logger.error(f"Fan-in service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-in service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-in service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_in_scoped_multi: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/fan-out-scoped-multi")
async def gateway_fan_out_scoped_multi(folder: UploadFile = File(...), scope: str = Form(...)):
    try:
        async with httpx.AsyncClient() as client:
            files = {"folder": (folder.filename, folder.file, folder.content_type)}
            data = {"scope": scope}
            
            logger.info(f"Forwarding multi-function scoped fan-out request for folder {folder.filename}")
            response = await client.post(
                f"{FANOUT_URL}/metrics/fan-out-scoped-multi",
                files=files,
                data=data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Multi-function scoped fan-out calculation successful")
                return result
            else:
                error_detail = response.json().get("detail", "Error from Fan-out service")
                logger.error(f"Fan-out service error: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to Fan-out service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Fan-out service is unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_fan_out_scoped_multi: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/combined-multi")
async def gateway_combined_multi_metrics(file: UploadFile = File(...), function_names: str = Form(...)):
    try:
        content = await file.read()
        
        async with httpx.AsyncClient() as client:
            fan_in_file = (file.filename, content, file.content_type)
            fan_out_file = (file.filename, content, file.content_type)
            
            fan_in_response, fan_out_response = await asyncio.gather(
                client.post(
                    f"{FANIN_URL}/metrics/fan-in-multi",
                    files={"file": fan_in_file},
                    data={"function_names": function_names}
                ),
                client.post(
                    f"{FANOUT_URL}/metrics/fan-out-multi",
                    files={"file": fan_out_file},
                    data={"function_names": function_names}
                )
            )
            
            if fan_in_response.status_code == 200 and fan_out_response.status_code == 200:
                fan_in_results = fan_in_response.json()
                fan_out_results = fan_out_response.json()
                
                combined_results = {}
                
                for function_name, fan_in_value in fan_in_results["results"].items():
                    if function_name not in combined_results:
                        combined_results[function_name] = {}
                    combined_results[function_name]["fan_in"] = fan_in_value
                
                for function_name, fan_out_value in fan_out_results["results"].items():
                    if function_name not in combined_results:
                        combined_results[function_name] = {}
                    combined_results[function_name]["fan_out"] = fan_out_value
                
                logger.info(f"Combined multi-function metrics calculation successful")
                return {"results": combined_results}
            else:
                if fan_in_response.status_code != 200:
                    error_detail = fan_in_response.json().get("detail", "Error from Fan-in service")
                    logger.error(f"Fan-in service error: {error_detail}")
                else:
                    error_detail = fan_out_response.json().get("detail", "Error from Fan-out service")
                    logger.error(f"Fan-out service error: {error_detail}")
                
                raise HTTPException(
                    status_code=500,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to services: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="One or more metrics services are unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_combined_multi_metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/metrics/combined-scoped-multi")
async def gateway_combined_scoped_multi_metrics(folder: UploadFile = File(...), scope: str = Form(...)):
    try:
        content = await folder.read()
        
        async with httpx.AsyncClient() as client:
            fan_in_file = (folder.filename, content, folder.content_type)
            fan_out_file = (folder.filename, content, folder.content_type)
            
            fan_in_response, fan_out_response = await asyncio.gather(
                client.post(
                    f"{FANIN_URL}/metrics/fan-in-scoped-multi",
                    files={"folder": fan_in_file},
                    data={"scope": scope},
                    timeout=60.0
                ),
                client.post(
                    f"{FANOUT_URL}/metrics/fan-out-scoped-multi",
                    files={"folder": fan_out_file},
                    data={"scope": scope},
                    timeout=60.0
                )
            )
            
            if fan_in_response.status_code == 200 and fan_out_response.status_code == 200:
                fan_in_results = fan_in_response.json()
                fan_out_results = fan_out_response.json()
                
                combined_results = {}
                

                for function_name, fan_in_data in fan_in_results["results"].items():
                    if function_name not in combined_results:
                        combined_results[function_name] = {
                            "per_file_results": {}
                        }
                    combined_results[function_name]["total_fan_in"] = fan_in_data["total_fan_in"]
                    

                    for file_path, file_fan_in in fan_in_data["per_file_results"].items():
                        if file_path not in combined_results[function_name]["per_file_results"]:
                            combined_results[function_name]["per_file_results"][file_path] = {}
                        combined_results[function_name]["per_file_results"][file_path]["fan_in"] = file_fan_in
                

                for function_name, fan_out_data in fan_out_results["results"].items():
                    if function_name not in combined_results:
                        combined_results[function_name] = {
                            "per_file_results": {}
                        }
                    combined_results[function_name]["total_fan_out"] = fan_out_data["total_fan_out"]
                    

                    for file_path, file_fan_out in fan_out_data["per_file_results"].items():
                        if file_path not in combined_results[function_name]["per_file_results"]:
                            combined_results[function_name]["per_file_results"][file_path] = {}
                        combined_results[function_name]["per_file_results"][file_path]["fan_out"] = file_fan_out
                
                logger.info(f"Combined scoped multi-function metrics calculation successful")
                return {"results": combined_results}
            else:
                if fan_in_response.status_code != 200:
                    error_detail = fan_in_response.json().get("detail", "Error from Fan-in service")
                    logger.error(f"Fan-in service error: {error_detail}")
                else:
                    error_detail = fan_out_response.json().get("detail", "Error from Fan-out service")
                    logger.error(f"Fan-out service error: {error_detail}")
                
                raise HTTPException(
                    status_code=500,
                    detail=error_detail
                )
    except httpx.RequestError as e:
        logger.error(f"Connection error to services: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="One or more metrics services are unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error in gateway_combined_scoped_multi_metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)