from domain.entities.query_result import QueryResult
from domain.repositories.database_repository import DatabaseRepositoryProtocol
from infrastructure.database.query_validator import QueryValidator
from infrastructure.exceptions.database_exceptions import ForbiddenQueryError


class ExecuteQueryUseCase:
    """Use case: Execute SQL SELECT query with security validation."""

    def __init__(
        self, repository: DatabaseRepositoryProtocol, query_validator: QueryValidator
    ) -> None:
        self._repository = repository
        self._query_validator = query_validator

    async def execute(self, query: str) -> QueryResult:
        """Execute SQL query with validation.

        Args:
            query: SQL query to execute

        Returns:
            Query execution result

        Raises:
            ForbiddenQueryError: If query contains forbidden operations
            QueryExecutionError: If query execution fails
        """
        # Validate query security
        if not self._query_validator.is_safe_query(query):
            forbidden_keyword = self._query_validator.get_forbidden_keyword(query)
            raise ForbiddenQueryError(f"Query contains forbidden keyword: {forbidden_keyword}")

        # Execute query
        return await self._repository.execute_query(query)
