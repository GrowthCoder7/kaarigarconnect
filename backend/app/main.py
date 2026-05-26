from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.automate import router as automate_router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="KaarigarConnect API", version="1.0.0")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(automate_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}