from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.schemas.report import ReportCreate, ReportRead
from api.services.moderation import create_report

router = APIRouter(prefix='/reports', tags=['reports'])


@router.post('', response_model=ReportRead, status_code=201)
async def create_report_endpoint(
    payload: ReportCreate,
    session: AsyncSession = Depends(get_session),
) -> ReportRead:
    return await create_report(session, payload)
