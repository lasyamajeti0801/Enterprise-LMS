"""Pagination utilities for SQLAlchemy query results."""

import math


class Page:
    """Dataclass holding paginated items and navigation metadata."""

    def __init__(self, items, page, per_page, total_count):
        self.items = items
        self.page = max(1, int(page))
        self.per_page = max(1, int(per_page))
        self.total_count = total_count
        self.total_pages = max(1, math.ceil(total_count / self.per_page))
        self.has_prev = self.page > 1
        self.has_next = self.page < self.total_pages
        self.prev_page = self.page - 1 if self.has_prev else None
        self.next_page = self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        """Yield page numbers with None representing ellipsis."""
        last = 0
        for num in range(1, self.total_pages + 1):
            if (
                num <= left_edge
                or (num > self.page - left_current - 1 and num < self.page + right_current)
                or num > self.total_pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def paginate_query(query, page=1, per_page=15) -> Page:
    """Apply offset and limit pagination to an active SQLAlchemy query."""
    page = int(page) if page else 1
    per_page = int(per_page) if per_page else 15
    total_count = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return Page(items=items, page=page, per_page=per_page, total_count=total_count)
