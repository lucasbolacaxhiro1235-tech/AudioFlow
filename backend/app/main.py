import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# DEBUG LOGS - These will appear in the Railway logs
print("\n" + "="*50)
print(f"DEBUG: Current Working Directory: {os.getcwd()}")
print(f"DEBUG: sys.path: {sys.path}")
try:
    import os
    print(f"DEBUG: Directory listing of root: {os.listdir('/')}")
    print(f"DEBUG: Directory listing of /app: {os.listdir('/app')}")
except Exception as e:
    print(f"DEBUG: Error listing directories: {e}")
print("="*50 + "\n")

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# ... (existing imports)
from app.api import admin, auth, downloads, library, me, plans, playlists

# --- BACKWARD COMPATIBILITY LAYER ---
@app.post("/api/call")
async def legacy_call(request: Request):
    body = await request.json()
    method = body.get("method")
    args = body.get("args", [])

    if method == "fetch_meta":
        # Redireciona para a lógica de resolve do downloads
        from app.services import metadata
        url = args[0] if args else ""
        return {"ok": True, "result": await metadata.resolve_url(url)}
    
    if method == "download":
        # O download agora requer autenticação e payload específico, 
        # então vamos disparar um erro claro se não estiver logado
        return JSONResponse(status_code=400, content={"ok": False, "error": "Use a API de downloads moderna (/api/downloads)"})
    
    return JSONResponse(status_code=404, content={"ok": False, "error": f"Método {method} não suportado"})
# ------------------------------------

# ... (rest of the file)
from app.config import cors_origins, settings
from app.database import init_db

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        await init_db()
        logger.info("Database ready")
    except Exception as exc:
        logger.error("Database init failed: %s", exc)
        raise

    try:
        from app.services.bootstrap import seed_first_admin, seed_plans

        if settings.SEED_PLANS:
            await seed_plans()
        await seed_first_admin()
    except Exception as exc:
        logger.warning("Bootstrap skipped: %s", exc)

    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AudioFlow API",
    description="Modern SaaS audio platform API — downloads, library and playlist management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication & account management"},
        {"name": "me", "description": "Current user"},
        {"name": "user", "description": "User stats"},
        {"name": "downloads", "description": "Download jobs"},
        {"name": "library", "description": "User audio library"},
        {"name": "playlists", "description": "Playlists"},
        {"name": "plans", "description": "Subscription plans"},
        {"name": "admin", "description": "Administration panel"},
        {"name": "health", "description": "Health checks"},
    ],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", tags=["health"])
async def root():
    return {"name": "AudioFlow API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": settings.APP_NAME}


# Serve local media storage when backend is local
if settings.STORAGE_BACKEND.lower() == "local":
    media_path = Path(settings.STORAGE_LOCAL_PATH).resolve()
    media_path.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_path)), name="media")


app.include_router(auth.router, prefix="/api")
app.include_router(me.me_router, prefix="/api")
app.include_router(me.user_router, prefix="/api")
app.include_router(downloads.router, prefix="/api")
app.include_router(library.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(admin.router, prefix="/api")