"""Tool for executing SQL queries against database."""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

import httpx
from pydantic import Field
from sgr_agent_core.base_tool import BaseTool

# API URL configurable via environment variable (for Docker)
SQL_API_BASE_URL = os.environ.get("SQL_API_URL", "http://localhost:18790")

if TYPE_CHECKING:
    from sgr_agent_core.agent_definition import AgentConfig
    from sgr_agent_core.models import AgentContext

logger = logging.getLogger(__name__)


class SQLDatabaseExecuteQueryTool(BaseTool):
    """Execute SQL SELECT queries against PostgreSQL and return results.

    Supports: SELECT with WHERE, aggregations (COUNT/SUM/AVG), GROUP BY, ORDER BY, JOINs, CTEs, LIMIT/OFFSET.

    SECURITY: Only SELECT queries allowed. INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER/CREATE are forbidden.

    Best practices:
    1. ALWAYS use LIMIT for result limiting (especially during exploration)
    2. Use SQLTableGetSchemaTool BEFORE writing query
    3. Check column data types for proper WHERE formatting
    4. Use single quotes for strings: WHERE name = 'value'
    5. Use proper date format: WHERE date > '2024-01-01'

    Good query examples:
    - SELECT * FROM dict_currencies LIMIT 10
    - SELECT log_level, COUNT(*) FROM app_logs GROUP BY log_level
    - SELECT * FROM app_logs WHERE created_at > NOW() - INTERVAL '1 day' LIMIT 50

    Returns: columns list, rows array, row count, executed query.

    NOTE: Use LIMIT and WHERE to control result size.
    """

    reasoning: str = Field(
        description="Why you need this query and what information it should return (2-3 sentences)"
    )
    sql_query: str = Field(
        description="SQL SELECT query to execute. Use LIMIT to limit results. Example: SELECT * FROM table_name WHERE condition LIMIT 10"
    )
    expected_columns: list[str] = Field(
        description="List of expected columns in result (for query validation)",
        default=[],
    )

    async def __call__(self, context: AgentContext, config: AgentConfig, **_) -> str:
        """Execute SQL query via API.

        Args:
            context: Agent context
            config: Agent configuration

        Returns:
            JSON string with query results
        """
        api_url = f"{SQL_API_BASE_URL}/api/query"

        logger.info("🔍 Executing SQL query")
        logger.debug(f"Reasoning: {self.reasoning}")
        logger.debug(f"Query: {self.sql_query}")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    json={"query": self.sql_query},
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

                result = response.json()

                # Validate expected columns if specified
                if self.expected_columns:
                    actual_columns = set(result.get("columns", []))
                    expected_columns = set(self.expected_columns)

                    if not expected_columns.issubset(actual_columns):
                        missing = expected_columns - actual_columns
                        logger.warning(f"⚠️ Some expected columns are missing: {missing}")

                # Add summary for convenience
                summary = {
                    "row_count": result["row_count"],
                    "column_count": len(result["columns"]),
                    "columns": result["columns"],
                    "has_data": result["row_count"] > 0,
                }

                # Warn if too much data
                if result["row_count"] > 100:
                    summary["warning"] = (
                        f"Returned {result['row_count']} rows. "
                        "Consider using LIMIT to restrict results."
                    )

                formatted_result = {
                    "summary": summary,
                    "data": {
                        "columns": result["columns"],
                        "rows": result["rows"],
                    },
                    "query_executed": result.get("query", self.sql_query),
                }

                logger.info(
                    f"✅ Query executed successfully: {result['row_count']} rows, "
                    f"{len(result['columns'])} columns"
                )

                # Add hint if no data
                if result["row_count"] == 0:
                    formatted_result["hint"] = (
                        "Query executed successfully but returned no data. "
                        "Check WHERE conditions or try different query."
                    )

                return json.dumps(formatted_result, ensure_ascii=False, indent=2)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Forbidden query type or validation error
                try:
                    error_detail = e.response.json().get("detail", str(e))
                except Exception:
                    error_detail = str(e)

                error_msg = f"SQL query validation error: {error_detail}"
                logger.error(error_msg)

                return json.dumps(
                    {
                        "error": error_msg,
                        "hint": "Check that query starts with SELECT and doesn't contain forbidden operations (INSERT, UPDATE, DELETE, DROP, etc.)",
                        "query": self.sql_query,
                    },
                    ensure_ascii=False,
                )
            elif e.response.status_code == 500:
                # SQL execution error
                try:
                    error_detail = e.response.json().get("detail", str(e))
                except Exception:
                    error_detail = str(e)

                error_msg = f"SQL query execution error: {error_detail}"
                logger.error(error_msg)

                # Try to provide helpful hints
                hints = []
                if "does not exist" in error_detail.lower():
                    hints.append("Table or column doesn't exist. Use SQLDatabaseGetTablesTool and SQLTableGetSchemaTool to verify.")
                if "syntax error" in error_detail.lower():
                    hints.append("SQL syntax error. Check query syntax.")
                if "permission denied" in error_detail.lower():
                    hints.append("Insufficient permissions to execute query.")

                return json.dumps(
                    {
                        "error": error_msg,
                        "hints": hints if hints else ["Check SQL query syntax"],
                        "query": self.sql_query,
                    },
                    ensure_ascii=False,
                )
            else:
                error_msg = f"HTTP error executing query: {e.response.status_code}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg, "details": str(e)}, ensure_ascii=False)

        except httpx.RequestError as e:
            error_msg = f"Database API connection error: {str(e)}"
            logger.error(error_msg)
            return json.dumps(
                {"error": error_msg, "hint": f"Check that API is running on {SQL_API_BASE_URL}"},
                ensure_ascii=False,
            )
        except Exception as e:
            error_msg = f"Unexpected error executing query: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
