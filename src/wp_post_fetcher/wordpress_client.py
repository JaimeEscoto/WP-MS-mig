"""WordPress REST API client."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Generator, List, Mapping, Optional

import requests

from .config import WordPressConfig

logger = logging.getLogger(__name__)


class WordPressClient:
    """Minimal client for the WordPress REST API."""

    def __init__(self, config: WordPressConfig) -> None:
        self._config = config
        self._session = requests.Session()
        if config.username and config.application_password:
            self._session.auth = (config.username, config.application_password)

    def fetch_posts(self) -> List[Mapping[str, object]]:
        """Retrieve posts created on or after the configured date."""
        after = self._format_after(self._config.date)
        posts: List[Mapping[str, object]] = []
        for batch in self._fetch_paginated(after=after, per_page=self._config.per_page):
            posts.extend(batch)
        return [self._extract_fields(post) for post in posts]

    def _fetch_paginated(
        self, *, after: str, per_page: int
    ) -> Generator[List[Mapping[str, object]], None, None]:
        page = 1
        while True:
            params = {
                "after": after,
                "page": page,
                "per_page": min(per_page, 100),
                "orderby": "date",
                "order": "asc",
                "_fields": ",".join(
                    [
                        "id",
                        "date",
                        "slug",
                        "status",
                        "type",
                        "link",
                        "title.rendered",
                        "content.rendered",
                        "excerpt.rendered",
                    ]
                ),
            }
            url = f"{self._config.base_url}/wp-json/wp/v2/posts"
            response = self._session.get(url, params=params, timeout=30)
            if response.status_code == 400:
                try:
                    error = response.json()
                except ValueError:  # not JSON
                    response.raise_for_status()
                    continue
                if error.get("code") == "rest_post_invalid_page_number":
                    break
                response.raise_for_status()
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            logger.debug("Fetched %s posts from page %s", len(data), page)
            yield data
            page += 1

    @staticmethod
    def _format_after(date_str: str) -> str:
        date = datetime.fromisoformat(date_str)
        return date.strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def _extract_fields(post: Mapping[str, object]) -> Mapping[str, object]:
        return {
            "id": post.get("id"),
            "date": post.get("date"),
            "slug": post.get("slug"),
            "status": post.get("status"),
            "type": post.get("type"),
            "link": post.get("link"),
            "title": WordPressClient._get_nested(post, "title", "rendered"),
            "content": WordPressClient._get_nested(post, "content", "rendered"),
            "excerpt": WordPressClient._get_nested(post, "excerpt", "rendered"),
        }

    @staticmethod
    def _get_nested(data: Mapping[str, object], *keys: str) -> Optional[object]:
        current: Optional[object] = data
        for key in keys:
            if not isinstance(current, Mapping) or key not in current:
                return None
            current = current[key]
        return current
