from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import ItemType
from api.schemas.item import CategoryResponse, SourceRead
from api.services.verification import list_sources_for_item

router = APIRouter(tags=['sources'])


@router.get('/sources/{item_id}', response_model=list[SourceRead])
async def get_sources(item_id: str, session: AsyncSession = Depends(get_session)) -> list[SourceRead]:
    sources = await list_sources_for_item(session, item_id)
    if not sources:
        raise HTTPException(status_code=404, detail='No sources found for item')
    return sources


@router.get('/categories', response_model=CategoryResponse)
async def get_categories() -> CategoryResponse:
    return CategoryResponse(categories=[item_type.value for item_type in ItemType])
