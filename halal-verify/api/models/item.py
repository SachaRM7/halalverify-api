from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class ItemType(str, Enum):
    food = 'food'
    cosmetic = 'cosmetic'
    restaurant = 'restaurant'
    ingredient = 'ingredient'


class HalalStatus(str, Enum):
    halal = 'halal'
    haram = 'haram'
    questionable = 'questionable'
    unknown = 'unknown'


class ConfidenceLevel(str, Enum):
    verified = 'verified'
    community = 'community'
    unknown = 'unknown'


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[ItemType] = mapped_column(SqlEnum(ItemType), index=True)
    status: Mapped[HalalStatus] = mapped_column(SqlEnum(HalalStatus), index=True, default=HalalStatus.unknown)
    confidence: Mapped[ConfidenceLevel] = mapped_column(SqlEnum(ConfidenceLevel), default=ConfidenceLevel.unknown)
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    community_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sources: Mapped[list['Source']] = relationship(back_populates='item', cascade='all, delete-orphan')


class SourceType(str, Enum):
    certification = 'certification'
    scholar = 'scholar'
    community = 'community'


class Source(Base):
    __tablename__ = 'sources'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id', ondelete='CASCADE'), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(String(500))
    source_type: Mapped[SourceType] = mapped_column(SqlEnum(SourceType), default=SourceType.community)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[Item] = relationship(back_populates='sources')
