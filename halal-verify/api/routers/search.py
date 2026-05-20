from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import get_api_key
from api.core.rate_limit import limiter
from api.database import get_session
from api.models import ItemType
from api.schemas.common import PaginatedResponse
from api.schemas.item import SearchResult
from api.services.verification import search_items

router = APIRouter(tags=['search'])


@router.get('/search', response_model=PaginatedResponse[SearchResult])
@limiter.limit('100/minute')
async def search(
    request: Request,
    q: str = Query(..., min_length=1),
    type: ItemType | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Depends(get_api_key),
) -> PaginatedResponse[SearchResult]:
    results = await search_items(session, query=q, item_type=type, page=page, page_size=page_size)
    mapped = [
        SearchResult(
            item_id=item.id,
            name=item.name,
            type=item.type,
            status=item.status,
            confidence=item.confidence,
            updated_at=item.updated_at,
        )
        for item in results.items
    ]
    return PaginatedResponse(items=mapped, total=results.total, page=results.page, page_size=results.page_size)
