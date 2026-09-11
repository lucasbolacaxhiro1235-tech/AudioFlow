import os
import uuid
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

_DB = BACKEND_DIR / "_test.db"
if _DB.exists():
    _DB.unlink()

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_DB}")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("STORAGE_LOCAL_PATH", str(BACKEND_DIR / "storage_test"))
os.environ.setdefault("STORAGE_PUBLIC_BASE_URL", "http://localhost:8000/media")
os.environ.setdefault("REDIS_URL", "redis://localhost:6999/0")
os.environ.setdefault("ALLOW_ANONYMOUS", "true")
os.environ.setdefault("SEED_PLANS", "true")

import httpx
import pytest

from app.database import init_db
from app.services.bootstrap import seed_plans
from app.main import app


@pytest.fixture(autouse=True)
async def _setup():
    await init_db()
    await seed_plans()
    yield


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def visitor_a():
    return {"X-Client-Id": str(uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))}


@pytest.fixture
def visitor_b():
    return {"X-Client-Id": str(uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"))}


@pytest.fixture
def fresh_client():
    return {"X-Client-Id": str(uuid.uuid4())}