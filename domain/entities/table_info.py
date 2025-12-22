from dataclasses import dataclass


@dataclass(frozen=True)
class TableInfo:
    """Domain entity representing database table metadata."""

    table_name: str
    table_type: str
    table_size: str | None
    column_count: int
    table_comment: str | None
