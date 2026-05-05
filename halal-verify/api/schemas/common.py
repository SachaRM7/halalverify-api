from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class HealthResponse(BaseModel):
    status: str
    app: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    total_items: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    total_sources: int
    total_submissions: int
    total_reports: int
    generated_at: datetime
