from dataclasses import dataclass


@dataclass(frozen=True)
class Pagination:
    """Domain entity representing pagination metadata."""

    page: int
    page_size: int
    total_count: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages from count and size."""
        return (self.total_count + self.page_size - 1) // self.page_size

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET from page and size."""
        return (self.page - 1) * self.page_size
