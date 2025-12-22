from typing import Any

from pydantic import BaseModel, Field


# Tables endpoint response schemas
class TableResponse(BaseModel):
    """Single table metadata."""

    table_name: str
    table_type: str
    table_size: str | None
    column_count: int
    table_comment: str | None


class PaginationResponse(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_count: int
    total_pages: int


class TablesResponse(BaseModel):
    """Response for GET /api/tables."""

    tables: list[TableResponse]
    pagination: PaginationResponse


# Schema endpoint response schemas
class ColumnResponse(BaseModel):
    """Single column metadata."""

    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    column_comment: str | None


class IndexResponse(BaseModel):
    """Single index metadata."""

    index_name: str
    columns: list[str]
    is_unique: bool
    is_primary: bool


class SchemaResponse(BaseModel):
    """Response for GET /api/tables/{table_name}/schema."""

    table_name: str
    table_comment: str | None
    column_count: int
    columns: list[ColumnResponse]
    indexes: list[IndexResponse]


# Query endpoint response schemas
class QueryResponse(BaseModel):
    """Response for POST /api/query."""

    columns: list[str] = Field(description="Column names")
    rows: list[list[Any]] = Field(description="Query result rows")
    row_count: int = Field(description="Number of rows returned")


# Error response schema
class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
