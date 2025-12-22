import asyncpg  # type: ignore[import-untyped]

from domain.entities.column_info import ColumnInfo, IndexInfo
from domain.entities.pagination import Pagination
from domain.entities.query_result import QueryResult
from domain.entities.table_info import TableInfo
from infrastructure.database.connection import DatabaseConnectionPool
from infrastructure.exceptions.database_exceptions import QueryExecutionError, TableNotFoundError


class PostgreSQLRepository:
    """PostgreSQL implementation of DatabaseRepositoryProtocol."""

    def __init__(self, pool: DatabaseConnectionPool) -> None:
        self._pool = pool

    async def get_tables(  # type: ignore[return]
        self, pagination: Pagination
    ) -> tuple[list[TableInfo], int]:
        """Get paginated list of tables with metadata."""

        # Query for tables with metadata
        tables_query = """
            SELECT
                c.relname AS table_name,
                CASE c.relkind
                    WHEN 'r' THEN 'BASE TABLE'
                    WHEN 'v' THEN 'VIEW'
                    WHEN 'm' THEN 'MATERIALIZED VIEW'
                END AS table_type,
                pg_size_pretty(pg_total_relation_size(c.oid)) AS table_size,
                (
                    SELECT count(*) FROM pg_attribute
                    WHERE attrelid = c.oid AND attnum > 0 AND NOT attisdropped
                ) AS column_count,
                obj_description(c.oid, 'pg_class') AS table_comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind IN ('r', 'v', 'm')
            ORDER BY c.relname
            LIMIT $1 OFFSET $2
        """

        # Count query
        count_query = """
            SELECT count(*)
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind IN ('r', 'v', 'm')
        """

        async for conn in self._pool.acquire():
            # Get total count
            total_count = await conn.fetchval(count_query)

            # Get paginated tables
            rows = await conn.fetch(tables_query, pagination.page_size, pagination.offset)

            tables = [
                TableInfo(
                    table_name=row["table_name"],
                    table_type=row["table_type"],
                    table_size=row["table_size"],
                    column_count=row["column_count"],
                    table_comment=row["table_comment"],
                )
                for row in rows
            ]

            return tables, total_count

    async def get_table_schema(  # type: ignore[return]
        self, table_name: str
    ) -> tuple[list[ColumnInfo], list[IndexInfo], str | None]:
        """Get detailed schema for specific table."""

        # Check if table exists
        exists_query = """
            SELECT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relname = $1
            )
        """

        # Get table comment
        comment_query = """
            SELECT obj_description(c.oid, 'pg_class') AS table_comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname = $1
        """

        # Get columns
        columns_query = """
            SELECT
                a.attname AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                NOT a.attnotnull AS is_nullable,
                EXISTS (
                    SELECT 1 FROM pg_constraint con
                    WHERE con.conrelid = a.attrelid
                      AND con.contype = 'p'
                      AND a.attnum = ANY(con.conkey)
                ) AS is_primary_key,
                EXISTS (
                    SELECT 1 FROM pg_constraint con
                    WHERE con.conrelid = a.attrelid
                      AND con.contype = 'f'
                      AND a.attnum = ANY(con.conkey)
                ) AS is_foreign_key,
                col_description(a.attrelid, a.attnum) AS column_comment,
                a.attnum AS ordinal_position
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = 'public'
              AND c.relname = $1
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
        """

        # Get indexes
        indexes_query = """
            SELECT
                i.relname AS index_name,
                ARRAY_AGG(a.attname ORDER BY a.attnum) AS columns,
                ix.indisunique AS is_unique,
                ix.indisprimary AS is_primary
            FROM pg_index ix
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_namespace n ON t.relnamespace = n.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE n.nspname = 'public' AND t.relname = $1
            GROUP BY i.relname, ix.indisunique, ix.indisprimary
        """

        async for conn in self._pool.acquire():
            # Check existence
            exists = await conn.fetchval(exists_query, table_name)
            if not exists:
                raise TableNotFoundError(f"Table '{table_name}' not found")

            # Get table comment
            table_comment = await conn.fetchval(comment_query, table_name)

            # Get columns
            column_rows = await conn.fetch(columns_query, table_name)
            columns = [
                ColumnInfo(
                    column_name=row["column_name"],
                    data_type=row["data_type"],
                    is_nullable=row["is_nullable"],
                    is_primary_key=row["is_primary_key"],
                    is_foreign_key=row["is_foreign_key"],
                    column_comment=row["column_comment"],
                    ordinal_position=row["ordinal_position"],
                )
                for row in column_rows
            ]

            # Get indexes
            index_rows = await conn.fetch(indexes_query, table_name)
            indexes = [
                IndexInfo(
                    index_name=row["index_name"],
                    columns=list(row["columns"]),
                    is_unique=row["is_unique"],
                    is_primary=row["is_primary"],
                )
                for row in index_rows
            ]

            return columns, indexes, table_comment

    async def execute_query(self, query: str) -> QueryResult:  # type: ignore[return]
        """Execute SQL SELECT query and return results."""
        try:
            async for conn in self._pool.acquire():
                rows = await conn.fetch(query)

                if not rows:
                    return QueryResult(columns=[], rows=[], row_count=0)

                columns = list(rows[0].keys())
                data_rows = [list(row.values()) for row in rows]

                return QueryResult(columns=columns, rows=data_rows, row_count=len(rows))
        except asyncpg.PostgresError as e:
            raise QueryExecutionError(f"Query execution failed: {str(e)}") from e
