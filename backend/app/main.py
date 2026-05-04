from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, builder, chat, scraping
from app.services.auth_service import get_current_active_user
from app.logging_config import configure_logging, get_logger
configure_logging()
logger = get_logger(__name__)

# Create FastAPI app
ENABLE_OPENAPI = os.getenv("ENABLE_OPENAPI", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to replace deprecated on_event startup/shutdown.

    Initializes the database on startup and disposes the async engine on
    shutdown. This keeps behavior identical to the previous on_event handlers
    but uses the supported lifespan interface.
    """
    logger.info("Starting up application...")
    # Initialize database tables and create admin user (synchronous helper)
    from app.init_db import init_database
    init_database()
    logger.info("Async database engine initialized")

    try:
        yield
    finally:
        logger.info("Shutting down application...")
        from app.database import async_engine
        await async_engine.dispose()
        logger.info("Async database engine disposed")

# By default disable automatic OpenAPI/docs in non-dev environments. Set
# ENABLE_OPENAPI=true to enable docs for development.
app = FastAPI(
    title="Analytics Tool API",
    description="API for managing scheduled Shodan searches and results",
    version="1.0.0",
    docs_url=("/docs" if ENABLE_OPENAPI else None),
    redoc_url=("/redoc" if ENABLE_OPENAPI else None),
    openapi_url=("/openapi.json" if ENABLE_OPENAPI else None),
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
# app.include_router(chat.router, prefix="/api", dependencies=[Depends(get_current_active_user)])
app.include_router(scraping.router)
app.include_router(builder.router)



@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Analytics Tool API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
