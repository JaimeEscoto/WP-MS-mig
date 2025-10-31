"""Configuration helpers for the WordPress post fetcher."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class WordPressConfig:
    """Settings required to reach a WordPress instance."""

    base_url: str
    username: Optional[str]
    application_password: Optional[str]
    date: str
    per_page: int


@dataclass
class DatabaseConfig:
    """Settings for the target SQLite database."""

    path: Path


@dataclass
class AppConfig:
    """Container for application configuration sections."""

    wordpress: WordPressConfig
    database: DatabaseConfig

    @classmethod
    def from_file(cls, config_path: Path) -> "AppConfig":
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        parser = configparser.ConfigParser()
        with config_path.open() as fp:
            parser.read_file(fp)

        if "wordpress" not in parser or "database" not in parser:
            raise ValueError("Configuration must include [wordpress] and [database] sections.")

        wordpress_section = parser["wordpress"]
        database_section = parser["database"]

        per_page = wordpress_section.getint("per_page", fallback=100)
        if per_page <= 0:
            raise ValueError("The 'per_page' setting must be a positive integer.")

        wordpress_config = WordPressConfig(
            base_url=wordpress_section.get("base_url", fallback="").rstrip("/"),
            username=wordpress_section.get("username"),
            application_password=wordpress_section.get("application_password"),
            date=wordpress_section.get("date", fallback=""),
            per_page=per_page,
        )

        if not wordpress_config.base_url:
            raise ValueError("The 'base_url' setting in the [wordpress] section is required.")
        if not wordpress_config.date:
            raise ValueError("The 'date' setting in the [wordpress] section is required.")

        database_config = DatabaseConfig(
            path=Path(database_section.get("path", fallback="data/wp_posts.db")),
        )

        return cls(wordpress=wordpress_config, database=database_config)
