from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="FasalSaathi AI Service", version="1.0.0")

# CORS – allow Express backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route imports (uncomment as you add them)
# from app.routes import predict

@app.get("/")
def home():
    return {"message": "FasalSaathi AI Service is running..."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
