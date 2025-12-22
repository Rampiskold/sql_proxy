from collections.abc import AsyncGenerator

import asyncpg  # type: ignore[import-untyped]

from infrastructure.config.settings import Settings


class DatabaseConnectionPool:
    """Manages asyncpg connection pool lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(
            self._settings.database_url,
            min_size=self._settings.db_pool_min_size,
            max_size=self._settings.db_pool_max_size,
            timeout=self._settings.db_pool_timeout,
        )

    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()

    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire connection from pool."""
        if not self._pool:
            raise RuntimeError("Connection pool not initialized")

        async with self._pool.acquire() as connection:
            yield connection


# Global pool instance
_pool: DatabaseConnectionPool | None = None


def get_pool(settings: Settings) -> DatabaseConnectionPool:
    """Get global connection pool instance."""
    global _pool
    if _pool is None:
        _pool = DatabaseConnectionPool(settings)
    return _pool
