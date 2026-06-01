"""AI Music Producer — API Gateway (Production Ready)

Main FastAPI application entry point with proper lifecycle management,
connection pooling, and graceful shutdown.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as aioredis
import structlog

from app.routers import beats, genres, jobs, analytics, trends, shopify, auth
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from shared.db.database import init_db, close_db, engine
from shared.utils.security import decode_access_token

logger = structlog.get_logger()

# ─── Global State ────────────────────────────────────────────────

class AppState:
    """Shared application state with connection pooling."""
    redis_pool: aioredis.Redis = None
    active_websockets: Set[WebSocket] = set()
    websocket_lock = asyncio.Lock()

state = AppState()

# ─── Lifespan ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with proper initialization and cleanup."""
    logger.info("api_gateway_starting", app_name="AI Music Producer")
    
    # Initialize database
    try:
        await init_db()
        logger.info("database_connected")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        raise
    
    # Initialize Redis connection pool
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    try:
        state.redis_pool = aioredis.from_url(
            redis_url,
            encoding='utf-8',
            decode_responses=True,
            max_connections=20,
        )
        await state.redis_pool.ping()
        logger.info("redis_connected", url=redis_url)
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        state.redis_pool = None
    
    logger.info("api_gateway_ready")
    yield
    
    # Graceful shutdown
    logger.info("api_gateway_shutting_down")
    
    # Close all WebSocket connections
    async with state.websocket_lock:
        for ws in list(state.active_websockets):
            try:
                await ws.close()
            except Exception:
                pass
        state.active_websockets.clear()
    
    # Close Redis pool
    if state.redis_pool:
        await state.redis_pool.close()
        logger.info("redis_disconnected")
    
    # Close database
    await close_db()
    logger.info("database_disconnected")
    
    logger.info("api_gateway_shutdown_complete")


# ─── App Initialization ────────────────────────────────────────────

app = FastAPI(
    title="AI Music Producer API",
    description="Autonomous AI music production platform",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware (order matters!)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - restrictive by default
environment = os.getenv('ENVIRONMENT', 'development')
if environment == 'production':
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
else:
    allowed_origins = ['http://localhost:3000', 'http://127.0.0.1:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['Authorization', 'Content-Type', 'X-Request-ID'],
)

# ─── Request ID Middleware ─────────────────────────────────────────

@app.middleware("http")
async def add_request_id(request, call_next):
    """Add request ID for distributed tracing."""
    import uuid
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    return response


# ─── Routers ───────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(beats.router, prefix="/api/v1/beats", tags=["Beats"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Genres"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Render Jobs"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(trends.router, prefix="/api/v1/trends", tags=["Trends"])
app.include_router(shopify.router, prefix="/api/v1/shopify", tags=["Shopify"])


# ─── Health Check ──────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "timestamp": structlog.contextvars.get_contextvars().get('timestamp')
    }


@app.get("/api/v1/health/detailed", tags=["Health"])
async def detailed_health():
    """Detailed health check with dependency status."""
    health = {
        "status": "healthy",
        "service": "api-gateway",
        "dependencies": {}
    }
    
    # Check Redis
    if state.redis_pool:
        try:
            await state.redis_pool.ping()
            health["dependencies"]["redis"] = "healthy"
        except Exception as e:
            health["dependencies"]["redis"] = f"unhealthy: {str(e)}"
            health["status"] = "degraded"
    else:
        health["dependencies"]["redis"] = "not_connected"
        health["status"] = "degraded"
    
    # Check Database (using existing engine pool)
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            health["dependencies"]["database"] = "healthy"
    except Exception as e:
        health["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    return health


# ─── WebSocket (Authenticated) ─────────────────────────────────────

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Authenticated WebSocket for real-time dashboard updates."""
    
    # Authenticate via query parameter or header
    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await websocket.accept()
    
    async with state.websocket_lock:
        state.active_websockets.add(websocket)
    
    logger.info(
        "websocket_connected",
        user_id=payload.get("sub"),
        total_connections=len(state.active_websockets)
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle subscription requests
            if data.get("action") == "subscribe":
                channel = data.get("channel", "all")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel,
                    "request_id": data.get("request_id")
                })
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("websocket_error", error=str(e))
    finally:
        async with state.websocket_lock:
            state.active_websockets.discard(websocket)
        
        logger.info(
            "websocket_disconnected",
            user_id=payload.get("sub"),
            total_connections=len(state.active_websockets)
        )


async def broadcast_to_websockets(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    disconnected = set()
    
    async with state.websocket_lock:
        for ws in state.active_websockets:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            state.active_websockets.discard(ws)


# ─── Root ──────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """API root."""
    return {
        "name": "AI Music Producer API",
        "version": "1.0.0",
        "environment": environment,
        "docs": "/docs",
        "health": "/health"
    }


# ─── Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
