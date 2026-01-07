"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Omni2 Admin Dashboard API...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")
    await close_db()
    print("✅ Database closed")


# Create FastAPI app
app = FastAPI(
    title="Omni2 Admin Dashboard API",
    description="Admin dashboard backend for Omni2 MCP Hub",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Omni2 Admin Dashboard API",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.api.v1 import auth
from app.api.v1 import dashboard
from app.api.v1 import chat
from app.api.v1 import chat_sessions
from app.api.v1 import omni2_health

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(chat_sessions.router, prefix="/api/v1/chat", tags=["Chat Sessions"])
app.include_router(omni2_health.router, prefix="/api/v1/omni2", tags=["Omni2 Health"])

# Additional routers (to be added in next phases)
# from app.api.v1 import mcps, users, config, analytics, audit
# app.include_router(mcps.router, prefix="/api/v1/mcps", tags=["mcps"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# ...
