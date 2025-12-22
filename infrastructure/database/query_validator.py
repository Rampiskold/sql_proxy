import re


class QueryValidator:
    """Validates SQL queries for security constraints."""

    FORBIDDEN_KEYWORDS = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "GRANT",
        "REVOKE",
    ]

    def is_safe_query(self, query: str) -> bool:
        """Check if query contains only SELECT operations.

        Args:
            query: SQL query to validate

        Returns:
            True if query is safe (SELECT only)
        """
        query_upper = query.upper()

        # Check for forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            # Use word boundary to match whole words only
            pattern = rf"\b{keyword}\b"
            if re.search(pattern, query_upper):
                return False

        return True

    def get_forbidden_keyword(self, query: str) -> str | None:
        """Get first forbidden keyword found in query.

        Args:
            query: SQL query to check

        Returns:
            Forbidden keyword or None
        """
        query_upper = query.upper()

        for keyword in self.FORBIDDEN_KEYWORDS:
            pattern = rf"\b{keyword}\b"
            if re.search(pattern, query_upper):
                return keyword.lower()

        return None
