from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.schemas.submission import SubmissionCreate, SubmissionRead
from api.services.moderation import create_submission, get_submission

router = APIRouter(prefix='/submissions', tags=['submissions'])


@router.post('', response_model=SubmissionRead, status_code=201)
async def create_submission_endpoint(
    payload: SubmissionCreate,
    session: AsyncSession = Depends(get_session),
) -> SubmissionRead:
    return await create_submission(session, payload)


@router.get('/{submission_id}', response_model=SubmissionRead)
async def get_submission_endpoint(
    submission_id: str,
    session: AsyncSession = Depends(get_session),
) -> SubmissionRead:
    submission = await get_submission(session, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail='Submission not found')
    return submission
