import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AIOS API",
    description="AI Business Operating System Backend",
    version="1.0.0"
)

# Enable CORS for local frontend communication
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
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "status": "success",
        "filename": file.filename,
        "file_path": file_path,
        "message": "File uploaded successfully. Ready for analytics processing."
    }

# Placeholder route for Teammate 1 (Data & Analytics)
@app.get("/api/analytics/{filename}")
async def get_analytics(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    # TODO: Connect to app.services.analytics once feature/analytics branch is merged
    return {
        "status": "pending_integration",
        "message": "Analytics service route ready for feature/analytics merge."
    }

# Placeholder route for Teammate 2 (AI Engine)
@app.post("/api/generate-insights")
async def generate_insights():
    # TODO: Connect to app.services.ai_service once feature/ai-engine branch is merged
    return {
        "status": "pending_integration",
        "message": "AI service route ready for feature/ai-engine merge."
    }
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