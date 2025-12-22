"""Tool for retrieving detailed table schema."""

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


class SQLTableGetSchemaTool(BaseTool):
    """Get detailed schema of specified PostgreSQL table.

    Returns: table description, all columns with properties (name, data type, nullable, PK/FK, comments), indexes.

    Use when you need to:
    - Understand table structure before writing queries
    - Check available columns for SELECT
    - Verify data types for WHERE conditions
    - Find Primary Keys for JOINs

    Best practices:
    - Use BEFORE writing SQL queries
    - Check column_comment for column purpose
    - Verify is_nullable before using in WHERE
    - Don't check same table schema twice

    NOTE: Returns structure only, not data. Use SQLDatabaseExecuteQueryTool for data queries.
    """

    reasoning: str = Field(
        description="Why you need this table schema and how you'll use it (1-2 sentences)"
    )
    table_name: str = Field(
        description="Exact table name (e.g., 'dict_currencies', 'app_logs')"
    )

    async def __call__(self, context: AgentContext, config: AgentConfig, **_) -> str:
        """Execute API request to get table schema.

        Args:
            context: Agent context
            config: Agent configuration

        Returns:
            JSON string with detailed table schema
        """
        api_url = f"{SQL_API_BASE_URL}/api/tables/{self.table_name}/schema"

        logger.info(f"🔍 Getting schema for table: {self.table_name}")
        logger.debug(f"Reasoning: {self.reasoning}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url)
                response.raise_for_status()

                result = response.json()

                # Add summary for convenience
                summary = {
                    "table_name": result["table_name"],
                    "table_comment": result.get("table_comment"),
                    "total_columns": result["column_count"],
                    "has_primary_key": any(col.get("is_primary_key") for col in result["columns"]),
                    "has_foreign_keys": any(col.get("is_foreign_key") for col in result["columns"]),
                    "indexes_count": len(result["indexes"]),
                }

                # Group columns by type for better understanding
                columns_by_type = {}
                for col in result["columns"]:
                    data_type = col["data_type"]
                    if data_type not in columns_by_type:
                        columns_by_type[data_type] = []
                    columns_by_type[data_type].append(col["column_name"])

                formatted_result = {
                    "summary": summary,
                    "columns_by_type": columns_by_type,
                    "full_schema": result,
                }

                logger.info(
                    f"✅ Retrieved schema for '{self.table_name}': "
                    f"{result['column_count']} columns, {len(result['indexes'])} indexes"
                )

                return json.dumps(formatted_result, ensure_ascii=False, indent=2)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Table '{self.table_name}' not found in database"
                logger.error(error_msg)
                return json.dumps(
                    {
                        "error": error_msg,
                        "hint": "Use SQLDatabaseGetTablesTool to get list of available tables",
                    },
                    ensure_ascii=False,
                )
            else:
                error_msg = f"HTTP error retrieving table schema: {e.response.status_code}"
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
            error_msg = f"Unexpected error retrieving table schema: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
