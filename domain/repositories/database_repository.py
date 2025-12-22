from typing import Protocol

from domain.entities.column_info import ColumnInfo, IndexInfo
from domain.entities.pagination import Pagination
from domain.entities.query_result import QueryResult
from domain.entities.table_info import TableInfo


class DatabaseRepositoryProtocol(Protocol):
    """Protocol defining database operations interface.

    Infrastructure layer must implement this protocol.
    Domain and use cases depend only on this abstraction.
    """

    async def get_tables(self, pagination: Pagination) -> tuple[list[TableInfo], int]:
        """Get list of tables with pagination.

        Args:
            pagination: Pagination parameters

        Returns:
            Tuple of (list of tables, total count)
        """
        ...

    async def get_table_schema(
        self, table_name: str
    ) -> tuple[list[ColumnInfo], list[IndexInfo], str | None]:
        """Get detailed schema for specific table.

        Args:
            table_name: Name of the table

        Returns:
            Tuple of (columns, indexes, table_comment)

        Raises:
            TableNotFoundError: If table doesn't exist
        """
        ...

    async def execute_query(self, query: str) -> QueryResult:
        """Execute validated SQL SELECT query.

        Args:
            query: SQL SELECT query (pre-validated)

        Returns:
            Query execution result

        Raises:
            QueryExecutionError: If query fails
        """
        ...
