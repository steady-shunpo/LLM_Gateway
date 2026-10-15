import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from controller.admin import router as admin_router
from controller.chat import router as chat_router
from repository.database import init_db
from services.rateLimiter import checkCacheAlive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    checkCacheAlive()
    yield


app = FastAPI(
    title="LLM Gateway",
    description="LLM Gateway API Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(admin_router)



@app.get("/", summary="Root endpoint")
async def root():
    return {
        "message": "Welcome to LLM Gateway API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", summary="Health checkpoint", tags=["Health"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "llm-gateway",
        },
    )
