from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.models import SubmissionStatus
from api.schemas.common import ORMModel


class SubmissionCreate(BaseModel):
    item_id: str | None = None
    submitted_by: str = Field(..., min_length=2, max_length=255)
    submitted_data: dict[str, Any]


class SubmissionRead(ORMModel):
    id: str
    item_id: str | None = None
    submitted_by: str
    submitted_data: dict[str, Any]
    status: SubmissionStatus
    reviewed_by: str | None = None
    created_at: datetime
