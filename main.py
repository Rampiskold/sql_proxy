import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.exception_handlers import database_error_handler
from api.routes import query, tables
from infrastructure.config.settings import get_settings
from infrastructure.database.connection import get_pool
from infrastructure.exceptions.database_exceptions import DatabaseError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    settings = get_settings()
    pool = get_pool(settings)

    # Startup: connect to database
    await pool.connect()
    logging.info("Database connection pool initialized")

    yield

    # Shutdown: close database connections
    await pool.disconnect()
    logging.info("Database connection pool closed")


# Create FastAPI application
app = FastAPI(
    title="SQL Query Proxy API",
    description="REST API for PostgreSQL database introspection and querying",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers
app.add_exception_handler(DatabaseError, database_error_handler)

# Include routers
app.include_router(tables.router)
app.include_router(query.router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "sql-query-proxy"}
