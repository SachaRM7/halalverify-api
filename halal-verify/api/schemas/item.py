from datetime import datetime

from pydantic import BaseModel

from api.models import ConfidenceLevel, HalalStatus, ItemType, SourceType
from api.schemas.common import ORMModel


class SourceRead(ORMModel):
    id: str
    source_name: str
    source_url: str
    source_type: SourceType
    verified: bool
    created_at: datetime


class ItemRead(ORMModel):
    id: str
    name: str
    type: ItemType
    status: HalalStatus
    confidence: ConfidenceLevel
    barcode: str | None = None
    community_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class VerificationResponse(ItemRead):
    sources: list[SourceRead]


class SearchResult(BaseModel):
    item_id: str
    name: str
    type: ItemType
    status: HalalStatus
    confidence: ConfidenceLevel
    updated_at: datetime


class CategoryResponse(BaseModel):
    categories: list[str]
