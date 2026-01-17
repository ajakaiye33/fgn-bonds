"""Pydantic schemas for admin dashboard."""

from pydantic import BaseModel

from .application import ApplicationResponse


class AdminFilters(BaseModel):
    """Filters for admin queries."""

    applicant_types: list[str] | None = None
    tenors: list[str] | None = None
    start_date: str | None = None
    end_date: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    is_resident: bool | None = None
    payment_statuses: list[str] | None = None  # pending, paid, verified, rejected
    search: str | None = None


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SummaryResponse(BaseModel):
    """Dashboard summary metrics."""

    total_applications: int
    total_value: float
    average_value: float
    this_month_count: int
    by_applicant_type: dict[str, int]


class TypeAnalytics(BaseModel):
    """Analytics by applicant type."""

    type: str
    count: int
    total_value: float


class MonthAnalytics(BaseModel):
    """Analytics by month."""

    month: str
    count: int
    total_value: float


class TenorAnalytics(BaseModel):
    """Analytics by tenor."""

    tenor: str
    count: int
    total_value: float


class ValueDistribution(BaseModel):
    """Value distribution range."""

    range: str
    count: int


class AnalyticsResponse(BaseModel):
    """Analytics data for charts."""

    by_applicant_type: list[TypeAnalytics]
    by_month: list[MonthAnalytics]
    by_tenor: list[TenorAnalytics]
    value_distribution: list[ValueDistribution]
