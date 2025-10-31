"""SQLite helpers for storing WordPress posts."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Mapping


POST_FIELDS = (
    "id",
    "date",
    "slug",
    "status",
    "type",
    "link",
    "title",
    "content",
    "excerpt",
)


class Database:
    """Lightweight wrapper around an SQLite connection."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    slug TEXT,
                    status TEXT,
                    type TEXT,
                    link TEXT,
                    title TEXT,
                    content TEXT,
                    excerpt TEXT
                )
                """
            )

    def insert_posts(self, posts: Iterable[Mapping[str, object]]) -> None:
        records = [
            tuple(post.get(field) for field in POST_FIELDS)
            for post in posts
        ]
        with self._conn:
            self._conn.executemany(
                """
                INSERT INTO posts (
                    id, date, slug, status, type, link, title, content, excerpt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    date=excluded.date,
                    slug=excluded.slug,
                    status=excluded.status,
                    type=excluded.type,
                    link=excluded.link,
                    title=excluded.title,
                    content=excluded.content,
                    excerpt=excluded.excerpt
                """,
                records,
            )

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
