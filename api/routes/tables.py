from fastapi import APIRouter, HTTPException, Path, Query, status

from api.dependencies import GetSchemaUseCaseDep, GetTablesUseCaseDep
from api.schemas.responses import (
    ColumnResponse,
    IndexResponse,
    PaginationResponse,
    SchemaResponse,
    TableResponse,
    TablesResponse,
)
from infrastructure.exceptions.database_exceptions import TableNotFoundError

router = APIRouter(prefix="/api", tags=["tables"])


@router.get("/tables", response_model=TablesResponse)
async def get_tables(
    use_case: GetTablesUseCaseDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
) -> TablesResponse:
    """Get paginated list of database tables with metadata.

    Returns table name, type, size, column count, and comment for each table.
    """
    tables, pagination = await use_case.execute(page=page, page_size=page_size)

    return TablesResponse(
        tables=[
            TableResponse(
                table_name=t.table_name,
                table_type=t.table_type,
                table_size=t.table_size,
                column_count=t.column_count,
                table_comment=t.table_comment,
            )
            for t in tables
        ],
        pagination=PaginationResponse(
            page=pagination.page,
            page_size=pagination.page_size,
            total_count=pagination.total_count,
            total_pages=pagination.total_pages,
        ),
    )


@router.get("/tables/{table_name}/schema", response_model=SchemaResponse)
async def get_table_schema(
    use_case: GetSchemaUseCaseDep,
    table_name: str = Path(description="Table name"),
) -> SchemaResponse:
    """Get detailed schema for specific table.

    Returns columns with data types, constraints, and indexes.
    """
    try:
        columns, indexes, table_comment = await use_case.execute(table_name=table_name)
    except TableNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return SchemaResponse(
        table_name=table_name,
        table_comment=table_comment,
        column_count=len(columns),
        columns=[
            ColumnResponse(
                column_name=c.column_name,
                data_type=c.data_type,
                is_nullable=c.is_nullable,
                is_primary_key=c.is_primary_key,
                is_foreign_key=c.is_foreign_key,
                column_comment=c.column_comment,
            )
            for c in columns
        ],
        indexes=[
            IndexResponse(
                index_name=idx.index_name,
                columns=idx.columns,
                is_unique=idx.is_unique,
                is_primary=idx.is_primary,
            )
            for idx in indexes
        ],
    )
