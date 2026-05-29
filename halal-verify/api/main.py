from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from api.config import get_settings
from api.core.rate_limit import limiter
from api.database import AsyncSessionLocal, init_db
from api.routers import reports, search, sources, submissions, verify
from api.schemas.common import HealthResponse, StatsResponse
from api.services.verification import get_stats, seed_demo_data

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if settings.seed_demo_data:
        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)
    yield


app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    description='Open halal verification API for products, ingredients, and restaurants.',
    lifespan=lifespan,
)
app.state.limiter = limiter
app.include_router(verify.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
app.include_router(submissions.router, prefix=settings.api_prefix)
app.include_router(sources.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={'detail': 'Rate limit exceeded'})


@app.get('/health', response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status='ok', app=settings.app_name)


@app.get(f'{settings.api_prefix}/stats', response_model=StatsResponse, tags=['stats'])
async def stats() -> StatsResponse:
    async with AsyncSessionLocal() as session:
        return await get_stats(session)
