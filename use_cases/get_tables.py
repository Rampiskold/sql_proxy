from domain.entities.pagination import Pagination
from domain.entities.table_info import TableInfo
from domain.repositories.database_repository import DatabaseRepositoryProtocol


class GetTablesUseCase:
    """Use case: Get paginated list of database tables."""

    def __init__(self, repository: DatabaseRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, page: int, page_size: int) -> tuple[list[TableInfo], Pagination]:
        """Execute get tables use case.

        Args:
            page: Page number (1-based)
            page_size: Items per page (1-100)

        Returns:
            Tuple of (tables list, pagination info)
        """
        pagination = Pagination(page=page, page_size=page_size, total_count=0)
        tables, total_count = await self._repository.get_tables(pagination)

        pagination = Pagination(page=page, page_size=page_size, total_count=total_count)

        return tables, pagination
