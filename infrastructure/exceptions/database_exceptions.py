class DatabaseError(Exception):
    """Base exception for database errors."""

    pass


class TableNotFoundError(DatabaseError):
    """Raised when requested table doesn't exist."""

    pass


class QueryExecutionError(DatabaseError):
    """Raised when SQL query execution fails."""

    pass


class ForbiddenQueryError(DatabaseError):
    """Raised when query contains forbidden operations."""

    pass
