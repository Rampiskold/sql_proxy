from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnInfo:
    """Domain entity representing table column metadata."""

    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    column_comment: str | None
    ordinal_position: int


@dataclass(frozen=True)
class IndexInfo:
    """Domain entity representing table index metadata."""

    index_name: str
    columns: list[str]
    is_unique: bool
    is_primary: bool
