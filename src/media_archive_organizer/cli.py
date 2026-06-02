"""Command-line interface for the media archive organizer."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from media_archive_organizer.config import OrganizerConfig
from media_archive_organizer.logging_config import configure_logging
from media_archive_organizer.organizer import organize_media


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Organize local photo and video archives by date."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(os.getenv("MEDIA_INPUT_DIR", "data/sample/input")),
        help="Directory containing media files to scan.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.getenv("MEDIA_OUTPUT_DIR", "data/sample/output")),
        help="Directory where organized copies are written.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan organization actions without copying files.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("MEDIA_LOG_LEVEL", "INFO"),
        help="Logging level, for example INFO, WARNING, or ERROR.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the organizer CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)

    config = OrganizerConfig(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
    )
    result = organize_media(config)

    summary = (
        f"Scanned: {result.scanned} | Organized: {result.organized} | "
        f"Repeated: {result.repeated} | To check: {result.to_check} | "
        f"Already exists: {result.already_exists} | Skipped: {result.skipped} | "
        f"Errors: {result.errors}"
    )
    print(summary)

    return 1 if result.errors else 0
