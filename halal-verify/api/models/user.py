from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base


class UserRole(str, Enum):
    user = 'user'
    moderator = 'moderator'
    admin = 'admin'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    reputation_score: Mapped[int] = mapped_column(Integer, default=0)
    submission_count: Mapped[int] = mapped_column(Integer, default=0)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.user)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
