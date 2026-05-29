from datetime import datetime

from pydantic import BaseModel, Field

from api.models import ReportStatus
from api.schemas.common import ORMModel


class ReportCreate(BaseModel):
    item_id: str
    reporter_id: str = Field(..., min_length=2, max_length=255)
    reason: str = Field(..., min_length=4, max_length=1000)


class ReportRead(ORMModel):
    id: str
    item_id: str
    reporter_id: str
    reason: str
    status: ReportStatus
    created_at: datetime
