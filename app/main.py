import os
import shutil
import time
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AIOS_Backend")

# Import service functions from team modules
from app.services.analytics import parse_sales_csv
from app.services.ai_service import generate_insights_from_metrics
from app.routes import email_routes

app = FastAPI(
    title="AIOS API",
    description="AI Business Operating System Backend",
    version="1.0.0"
)
app.include_router(email_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"[{request.method}] {request.url.path} -> Status {response.status_code} ({process_time}ms)")
    return response

UPLOAD_DIR = "data/uploads"
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit
RETENTION_PERIOD_SECONDS = 86400  # 24 Hours

os.makedirs(UPLOAD_DIR, exist_ok=True)


def cleanup_old_files():
    """Background task to remove files older than the retention period."""
    now = time.time()
    try:
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path) and not filename.startswith("."):
                file_age = now - os.path.getmtime(file_path)
                if file_age > RETENTION_PERIOD_SECONDS:
                    os.remove(file_path)
                    logger.info(f"Auto-cleaned expired file: {filename}")
    except Exception as e:
        logger.error(f"Error during background file cleanup: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "AIOS Backend is running smoothly!"}


@app.post("/api/upload")
async def upload_sales_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...)
):
    background_tasks.add_task(cleanup_old_files)

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only CSV files (.csv) are allowed."
        )
    
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
    
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413, 
            detail="File size exceeds the maximum allowed limit of 5 MB."
        )
    
    await file.seek(0)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File '{file.filename}' uploaded successfully ({len(contents)} bytes).")
    except Exception as e:
        logger.error(f"Failed to save file '{file.filename}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
        
    return {
        "status": "success",
        "filename": file.filename,
        "file_path": file_path,
        "file_size_bytes": len(contents),
        "message": "File uploaded and validated successfully."
    }


@app.get("/api/storage-status")
async def get_storage_status():
    if not os.path.exists(UPLOAD_DIR):
        return {"total_files": 0, "total_size_bytes": 0}
    
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and not f.startswith(".")]
    total_bytes = sum(os.path.getsize(os.path.join(UPLOAD_DIR, f)) for f in files)
    
    return {
        "status": "success",
        "total_files": len(files),
        "total_size_bytes": total_bytes,
        "total_size_mb": round(total_bytes / (1024 * 1024), 2),
        "files": files
    }


@app.get("/api/analytics/{filename}")
async def get_analytics(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
    
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        metrics = parse_sales_csv(file_bytes)
        return {
            "status": "success",
            "filename": filename,
            "data": metrics
        }
    except ValueError as ve:
        logger.warning(f"Data processing validation error for {filename}: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"CSV Validation Error: {str(ve)}")
    except Exception as e:
        logger.error(f"Analytics failure for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics processing failed: {str(e)}")


@app.post("/api/generate-insights")
async def generate_insights_route(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
    
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        metrics = parse_sales_csv(file_bytes)
        insights = generate_insights_from_metrics(metrics)
        return {
            "status": "success",
            "insights": insights
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"CSV Validation Error: {str(ve)}")
    except Exception as e:
        logger.error(f"AI Generation failure for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Insights generation failed: {str(e)}")


@app.delete("/api/clear-uploads")
async def clear_uploads():
    if not os.path.exists(UPLOAD_DIR):
        return {"status": "success", "message": "Upload directory is already empty."}
    
    deleted_files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path) and not filename.startswith("."):
            os.remove(file_path)
            deleted_files.append(filename)
            
    logger.info(f"Cleared {len(deleted_files)} files from uploads.")
    return {
        "status": "success",
        "deleted_files_count": len(deleted_files),
        "deleted_files": deleted_files,
        "message": "Upload directory cleared successfully."
    }