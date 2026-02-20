"""Token Trail - FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cors_origins_list
from app.core.db import get_db
from app.routers import auth, public, instructor

app = FastAPI(
    title="Token Trail API",
    description="Code similarity detection for academic assignments",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",
)

# CORS - origins from env var CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health():
    """Health endpoint for readiness checks."""
    return {"status": "ok", "service": "token-trail-api"}



@app.on_event("startup")
async def _create_indexes():
    """Ensure useful MongoDB indexes exist on startup."""
    db = get_db()
    db.instructors.create_index("email", unique=True)
    db.assignments.create_index("assignmentKey", unique=True)


# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(instructor.router, prefix="/api")
