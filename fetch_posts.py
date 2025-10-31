"""CLI utility to load WordPress posts into a local SQLite database."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from wp_post_fetcher import AppConfig, Database, WordPressClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.ini"),
        help="Path to the configuration file (default: config.ini)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    config = AppConfig.from_file(args.config)
    client = WordPressClient(config.wordpress)
    posts = client.fetch_posts()

    if not posts:
        logging.info("No posts found for the given date filter.")
        return

    with Database(config.database.path) as db:
        db.insert_posts(posts)
        logging.info("Stored %s posts in %s", len(posts), config.database.path)


if __name__ == "__main__":
    main()
