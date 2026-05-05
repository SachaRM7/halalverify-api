from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import get_api_key
from api.core.rate_limit import limiter
from api.database import get_session
from api.models import ItemType
from api.schemas.item import VerificationResponse
from api.services.verification import get_item_by_barcode, get_item_by_name

router = APIRouter(prefix='/verify', tags=['verify'])


@router.get('/barcode/{upc}', response_model=VerificationResponse)
@limiter.limit('100/minute')
async def verify_barcode(
    request: Request,
    upc: str = Path(..., min_length=6, max_length=32),
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Depends(get_api_key),
) -> VerificationResponse:
    item = await get_item_by_barcode(session, upc)
    if not item:
        raise HTTPException(status_code=404, detail='Barcode not found')
    return item


@router.get('/product/{name}', response_model=VerificationResponse)
@limiter.limit('100/minute')
async def verify_product(
    request: Request,
    name: str,
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Depends(get_api_key),
) -> VerificationResponse:
    item = await get_item_by_name(session, ItemType.food, name)
    if not item:
        raise HTTPException(status_code=404, detail='Product not found')
    return item


@router.get('/restaurant/{name}', response_model=VerificationResponse)
@limiter.limit('100/minute')
async def verify_restaurant(
    request: Request,
    name: str,
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Depends(get_api_key),
) -> VerificationResponse:
    item = await get_item_by_name(session, ItemType.restaurant, name)
    if not item:
        raise HTTPException(status_code=404, detail='Restaurant not found')
    return item


@router.get('/ingredient/{name}', response_model=VerificationResponse)
@limiter.limit('100/minute')
async def verify_ingredient(
    request: Request,
    name: str,
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Depends(get_api_key),
) -> VerificationResponse:
    item = await get_item_by_name(session, ItemType.ingredient, name)
    if not item:
        raise HTTPException(status_code=404, detail='Ingredient not found')
    return item
