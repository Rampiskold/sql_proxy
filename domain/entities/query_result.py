from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueryResult:
    """Domain entity representing SQL query execution result."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
