import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from app.api import system, production

load_dotenv()

app = FastAPI(title="Human Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/v1")
app.include_router(production.router, prefix="/api/v1/prod")

@app.get("/")
def read_root():
    return {"message": "Welcome to Human Agent API"}

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8100))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
