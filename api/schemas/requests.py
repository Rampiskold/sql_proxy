from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for POST /api/query endpoint."""

    query: str = Field(
        description="SQL SELECT query to execute",
        min_length=1,
        examples=["SELECT * FROM users LIMIT 10"],
    )
