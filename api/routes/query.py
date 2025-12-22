from fastapi import APIRouter, HTTPException, status

from api.dependencies import ExecuteQueryUseCaseDep
from api.schemas.requests import QueryRequest
from api.schemas.responses import QueryResponse
from infrastructure.exceptions.database_exceptions import ForbiddenQueryError, QueryExecutionError

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    use_case: ExecuteQueryUseCaseDep,
) -> QueryResponse:
    """Execute SQL SELECT query.

    Only SELECT queries are allowed. INSERT, UPDATE, DELETE, DROP, etc. are forbidden.
    """
    try:
        result = await use_case.execute(query=request.query)
    except ForbiddenQueryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except QueryExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e

    return QueryResponse(
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
    )
