import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import service functions from team modules
from app.services.analytics import parse_sales_csv
from app.services.ai_service import generate_insights_from_metrics

app = FastAPI(
    title="AIOS API",
    description="AI Business Operating System Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "AIOS Backend is running smoothly!"}

@app.post("/api/upload")
async def upload_sales_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
    
    await file.seek(0)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "status": "success",
        "filename": file.filename,
        "file_path": file_path,
        "file_size_bytes": len(contents),
        "message": "File uploaded and validated successfully."
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
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Prints full traceback in VS Code terminal
        raise HTTPException(status_code=500, detail=f"Analytics error: {type(e).__name__} - {str(e)}")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Insights generation failed: {str(e)}")
    
@app.delete("/api/clear-uploads")
async def clear_uploads():
    if not os.path.exists(UPLOAD_DIR):
        return {"status": "success", "message": "Upload directory is already empty."}
    
    deleted_files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted_files.append(filename)
            
    return {
        "status": "success",
        "deleted_files_count": len(deleted_files),
        "deleted_files": deleted_files,
        "message": "Upload directory cleared successfully."
    }