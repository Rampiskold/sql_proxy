from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse

from infrastructure.exceptions.database_exceptions import DatabaseError


async def database_error_handler(
    request: Request, exc: Union[Exception, DatabaseError]
) -> JSONResponse:
    """Handle database-related exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )
