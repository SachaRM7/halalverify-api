from __future__ import annotations

from collections import Counter
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models import Item, ItemType, Report, Source, Submission
from api.schemas.common import PaginatedResponse, StatsResponse


DEMO_ITEMS = [
    {
        'name': 'Snickers Bar',
        'type': ItemType.food,
        'status': 'halal',
        'confidence': 'verified',
        'barcode': '040000001001',
        'community_notes': 'Contains dairy and chocolate ingredients reviewed through supplier certification.',
        'sources': [
            {
                'source_name': 'Islamic Services of America',
                'source_url': 'https://www.isahalal.com/',
                'source_type': 'certification',
                'verified': True,
            }
        ],
    },
    {
        'name': 'Marshmallow Gelatin Mix',
        'type': ItemType.ingredient,
        'status': 'questionable',
        'confidence': 'community',
        'barcode': '040000001002',
        'community_notes': 'Gelatin source has not been independently confirmed.',
        'sources': [
            {
                'source_name': 'Community review board',
                'source_url': 'https://example.org/community-review',
                'source_type': 'community',
                'verified': False,
            }
        ],
    },
    {
        'name': 'Sakura Tokyo Halal Ramen',
        'type': ItemType.restaurant,
        'status': 'halal',
        'confidence': 'verified',
        'barcode': None,
        'community_notes': 'Restaurant advertises halal chicken and no alcohol on menu.',
        'sources': [
            {
                'source_name': 'Local halal guide',
                'source_url': 'https://example.org/tokyo-halal-guide',
                'source_type': 'scholar',
                'verified': True,
            }
        ],
    },
]


async def seed_demo_data(session: AsyncSession) -> None:
    existing = await session.scalar(select(func.count()).select_from(Item))
    if existing:
        return

    for demo in DEMO_ITEMS:
        item_data = {key: value for key, value in demo.items() if key != 'sources'}
        sources = list(demo['sources'])
        item = Item(**item_data)
        for source in sources:
            item.sources.append(Source(**source))
        session.add(item)

    await session.commit()


async def get_item_by_barcode(session: AsyncSession, barcode: str) -> Item | None:
    stmt = select(Item).options(selectinload(Item.sources)).where(Item.barcode == barcode)
    return await session.scalar(stmt)


async def get_item_by_name(session: AsyncSession, item_type: ItemType, name: str) -> Item | None:
    stmt = (
        select(Item)
        .options(selectinload(Item.sources))
        .where(Item.type == item_type)
        .where(func.lower(Item.name) == name.lower())
    )
    return await session.scalar(stmt)


async def search_items(
    session: AsyncSession,
    query: str,
    item_type: ItemType | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[Item]:
    filters = [or_(Item.name.ilike(f'%{query}%'), Item.community_notes.ilike(f'%{query}%'))]
    if item_type:
        filters.append(Item.type == item_type)

    total_stmt = select(func.count()).select_from(Item).where(*filters)
    total = (await session.execute(total_stmt)).scalar_one()

    stmt = (
        select(Item)
        .where(*filters)
        .order_by(Item.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list((await session.scalars(stmt)).all())
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


async def list_sources_for_item(session: AsyncSession, item_id: str) -> list[Source]:
    stmt = select(Source).where(Source.item_id == item_id).order_by(Source.verified.desc(), Source.created_at.desc())
    return list((await session.scalars(stmt)).all())


async def get_stats(session: AsyncSession) -> StatsResponse:
    items = list((await session.scalars(select(Item))).all())
    types = Counter(getattr(item.type, 'value', item.type) for item in items)
    statuses = Counter(getattr(item.status, 'value', item.status) for item in items)
    total_sources = await session.scalar(select(func.count()).select_from(Source))
    total_submissions = await session.scalar(select(func.count()).select_from(Submission))
    total_reports = await session.scalar(select(func.count()).select_from(Report))
    return StatsResponse(
        total_items=len(items),
        by_type=dict(types),
        by_status=dict(statuses),
        total_sources=total_sources or 0,
        total_submissions=total_submissions or 0,
        total_reports=total_reports or 0,
        generated_at=datetime.utcnow(),
    )
