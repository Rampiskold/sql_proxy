from domain.entities.column_info import ColumnInfo, IndexInfo
from domain.repositories.database_repository import DatabaseRepositoryProtocol


class GetTableSchemaUseCase:
    """Use case: Get detailed schema for specific table."""

    def __init__(self, repository: DatabaseRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(
        self, table_name: str
    ) -> tuple[list[ColumnInfo], list[IndexInfo], str | None]:
        """Execute get table schema use case.

        Args:
            table_name: Name of the table

        Returns:
            Tuple of (columns, indexes, table_comment)

        Raises:
            TableNotFoundError: If table doesn't exist
        """
        return await self._repository.get_table_schema(table_name)
