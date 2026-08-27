from fastapi import FastAPI
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

@app.get("/")
def read_root():
    return {"status": "online", "message": "AIOS Backend Engine Running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}