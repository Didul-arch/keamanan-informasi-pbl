from pydantic import BaseModel


class ReportItemRequest(BaseModel):
    title: str
    description: str
    location: str
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image: str | None = None


class ReportFoundItemRequest(BaseModel):
    title: str
    description: str
    location: str
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image: str | None = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    category: str | None = None
    image: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    report_type: str
    status: str
    reporter_id: int
    created_at: str