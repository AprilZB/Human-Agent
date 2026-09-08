import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Human Agent API"),
    version=os.getenv("APP_VERSION", "1.0.0")
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Human Agent API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8100))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
