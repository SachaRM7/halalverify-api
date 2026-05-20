import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

TEST_DB = Path(__file__).resolve().parents[1] / 'test_halalverify.db'
os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{TEST_DB}'
os.environ['SEED_DEMO_DATA'] = 'true'

from api.main import app  # noqa: E402
from api.database import AsyncSessionLocal, init_db  # noqa: E402
from api.services.verification import seed_demo_data  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
def cleanup_test_db() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()
    yield
    if TEST_DB.exists():
        TEST_DB.unlink()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver') as async_client:
        yield async_client
