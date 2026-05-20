from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Report, Submission
from api.schemas.report import ReportCreate
from api.schemas.submission import SubmissionCreate


async def create_submission(session: AsyncSession, payload: SubmissionCreate) -> Submission:
    submission = Submission(
        item_id=payload.item_id,
        submitted_by=payload.submitted_by,
        submitted_data=payload.submitted_data,
    )
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    return submission


async def get_submission(session: AsyncSession, submission_id: str) -> Submission | None:
    return await session.scalar(select(Submission).where(Submission.id == submission_id))


async def create_report(session: AsyncSession, payload: ReportCreate) -> Report:
    report = Report(
        item_id=payload.item_id,
        reporter_id=payload.reporter_id,
        reason=payload.reason,
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report
