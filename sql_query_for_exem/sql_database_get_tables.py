"""Tool for retrieving database tables list with pagination."""

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


class SQLDatabaseGetTablesTool(BaseTool):
    """Get list of PostgreSQL tables with metadata and pagination.

    Returns: table name, type, size, column count, comment.

    Use when you need to:
    - Discover available tables in database
    - Find table by name or description
    - Get database structure overview

    Best practices:
    - Start with page_size=5-10 for quick overview
    - Check table_comment for purpose description
    - Use SQLTableGetSchemaTool next for detailed structure

    NOTE: Returns metadata only, not actual data. Use SQLDatabaseExecuteQueryTool for data queries.
    """

    reasoning: str = Field(
        description="Why you need tables list and what you'll do with it (1-2 sentences)"
    )
    page: int = Field(
        description="Page number for pagination (starts from 1)",
        default=1,
        ge=1,
    )
    page_size: int = Field(
        description="Tables per page (recommended 5-10 for overview, max 100)",
        default=10,
        ge=1,
        le=100,
    )

    async def __call__(self, context: AgentContext, config: AgentConfig, **_) -> str:
        """Execute API request to get tables list.

        Args:
            context: Agent context
            config: Agent configuration

        Returns:
            JSON string with tables list and pagination info
        """
        api_url = f"{SQL_API_BASE_URL}/api/tables"

        logger.info(f"📊 Getting tables list: page={self.page}, page_size={self.page_size}")
        logger.debug(f"Reasoning: {self.reasoning}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    api_url,
                    params={"page": self.page, "page_size": self.page_size},
                )
                response.raise_for_status()

                result = response.json()

                # Format result for better readability
                formatted_result = {
                    "tables": result["tables"],
                    "pagination": result["pagination"],
                    "summary": {
                        "total_tables": result["pagination"]["total_count"],
                        "showing": f"{len(result['tables'])} tables on page {self.page} of {result['pagination']['total_pages']}",
                    }
                }

                logger.info(f"✅ Retrieved {len(result['tables'])} of {result['pagination']['total_count']} tables")

                return json.dumps(formatted_result, ensure_ascii=False, indent=2)

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error retrieving tables: {e.response.status_code}"
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
            error_msg = f"Unexpected error retrieving tables: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
