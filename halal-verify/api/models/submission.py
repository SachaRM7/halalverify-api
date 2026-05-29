from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class SubmissionStatus(str, Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class Submission(Base):
    __tablename__ = 'submissions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str | None] = mapped_column(ForeignKey('items.id'), nullable=True)
    submitted_by: Mapped[str] = mapped_column(String(255))
    submitted_data: Mapped[dict] = mapped_column(JSON)
    status: Mapped[SubmissionStatus] = mapped_column(SqlEnum(SubmissionStatus), default=SubmissionStatus.pending)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
