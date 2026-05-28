from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, upload, extract, chat
from app.telemetry.setup import setup_telemetry

app = FastAPI(title="FinSight AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_telemetry(app)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(extract.router, prefix="/api/extract", tags=["extract"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
