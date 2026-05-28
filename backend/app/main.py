from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, upload, extract, chat, compare, financial
from app.db.session import init_db
from app.telemetry.setup import setup_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FinSight AI", version="0.1.0", lifespan=lifespan)

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
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(financial.router, prefix="/api/financial", tags=["financial"])
