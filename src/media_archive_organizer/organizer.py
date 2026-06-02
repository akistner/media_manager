"""Core file organization workflow."""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from shutil import copy2

from media_archive_organizer.config import OrganizerConfig
from media_archive_organizer.duplicates import calculate_checksum
from media_archive_organizer.metadata import MediaMetadata, collect_metadata
from media_archive_organizer.naming import build_media_stem, choose_trusted_date

logger = logging.getLogger(__name__)
DUPLICATE_NAME_MARKERS = ("copy", "copia", "duplicate", "duplicado")


@dataclass
class OrganizationResult:
    """Summary counters and actions for one organization run."""

    scanned: int = 0
    organized: int = 0
    repeated: int = 0
    to_check: int = 0
    skipped: int = 0
    already_exists: int = 0
    errors: int = 0
    actions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MediaItem:
    """Supported media file with collected metadata and checksum."""

    path: Path
    metadata: MediaMetadata
    checksum: str


def iter_files(input_dir: Path) -> list[Path]:
    """Return all files below the input directory in deterministic order."""

    return sorted(path for path in input_dir.rglob("*") if path.is_file())


def validate_directories(input_dir: Path, output_dir: Path) -> None:
    """Validate input and output directories before scanning."""

    if input_dir == output_dir:
        raise ValueError("Input and output directories must be different.")

    if output_dir.is_relative_to(input_dir):
        raise ValueError("Output directory cannot be inside the input directory.")


def destination_has_same_content(destination: Path, checksum: str) -> bool:
    """Return true when an existing destination has the same checksum."""

    return destination.exists() and calculate_checksum(destination) == checksum


def next_available_path(
    destination: Path,
    checksum: str,
    reserved_paths: set[Path],
) -> tuple[Path, bool]:
    """Return a non-conflicting path and whether the file already exists."""

    if destination not in reserved_paths:
        if destination_has_same_content(destination, checksum):
            return destination, True
        if not destination.exists():
            return destination, False

    counter = 2
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter:02d}{destination.suffix}"
        )
        if candidate not in reserved_paths:
            if destination_has_same_content(candidate, checksum):
                return candidate, True
            if not candidate.exists():
                return candidate, False
        counter += 1


def build_desired_destination(
    output_dir: Path,
    media_metadata: MediaMetadata,
    duplicate: bool,
) -> tuple[Path, bool]:
    """Build the desired destination path before conflict checks."""

    selected_date = choose_trusted_date(media_metadata.date_candidates)

    if selected_date is None:
        destination = output_dir / "to_check" / media_metadata.path.name
        return destination, True

    stem = build_media_stem(media_metadata, selected_date)
    relative_dir = Path(
        f"{selected_date.year}",
        f"{selected_date.month:02d}",
        f"{selected_date.day:02d}",
    )

    if duplicate:
        relative_dir = Path("repeated") / relative_dir

    destination = output_dir / relative_dir / f"{stem}.{media_metadata.extension}"
    return destination, False


def copy_media_file(source: Path, destination: Path, dry_run: bool) -> None:
    """Copy a media file to the destination unless this is a dry run."""

    if dry_run:
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)


def has_duplicate_name_marker(path: Path) -> bool:
    """Return true when a file name looks like an explicit copy."""

    normalized_name = re.sub(r"[^a-z0-9]+", " ", path.stem.lower())
    tokens = set(normalized_name.split())
    return any(marker in tokens for marker in DUPLICATE_NAME_MARKERS)


def best_date_priority(metadata: MediaMetadata) -> int:
    """Return the best available trusted date priority for canonical sorting."""

    priorities = [
        candidate.priority
        for candidate in metadata.date_candidates
        if candidate.trusted and candidate.value.year >= 2000
    ]
    return min(priorities, default=999)


def choose_canonical_item(group: list[MediaItem]) -> MediaItem:
    """Choose the best representative for a duplicate checksum group."""

    return min(
        group,
        key=lambda item: (
            has_duplicate_name_marker(item.path),
            best_date_priority(item.metadata),
            len(item.path.stem),
            item.path.name.lower(),
            str(item.path).lower(),
        ),
    )


def order_duplicate_group(group: list[MediaItem]) -> list[MediaItem]:
    """Return duplicate group items with the canonical item first."""

    canonical = choose_canonical_item(group)
    remaining = sorted(
        (item for item in group if item is not canonical),
        key=lambda item: (item.path.name.lower(), str(item.path).lower()),
    )
    return [canonical, *remaining]


def collect_supported_items(
    config: OrganizerConfig,
    result: OrganizationResult,
) -> list[MediaItem]:
    """Collect metadata and checksums for supported input files."""

    items: list[MediaItem] = []

    for path in iter_files(config.input_dir):
        result.scanned += 1

        try:
            media_metadata = collect_metadata(
                path=path,
                image_extensions=config.image_extensions,
                video_extensions=config.video_extensions,
            )

            if media_metadata.media_type == "unsupported":
                result.skipped += 1
                logger.info("Skipped unsupported file: %s", path.name)
                continue

            items.append(
                MediaItem(
                    path=path,
                    metadata=media_metadata,
                    checksum=calculate_checksum(path),
                )
            )

        except Exception as exc:
            result.errors += 1
            logger.exception("Failed to inspect %s: %s", path, exc)

    return items


def group_items_by_checksum(items: list[MediaItem]) -> list[list[MediaItem]]:
    """Group supported files by checksum in deterministic order."""

    grouped: dict[str, list[MediaItem]] = defaultdict(list)

    for item in items:
        grouped[item.checksum].append(item)

    return sorted(
        grouped.values(),
        key=lambda group: str(choose_canonical_item(group).path).lower(),
    )


def record_result(
    result: OrganizationResult,
    manual_review: bool,
    duplicate: bool,
    already_exists: bool,
) -> None:
    """Increment the correct result counter for one planned item."""

    if already_exists:
        result.already_exists += 1
    elif manual_review:
        result.to_check += 1
    elif duplicate:
        result.repeated += 1
    else:
        result.organized += 1


def organize_media(config: OrganizerConfig) -> OrganizationResult:
    """Organize media files according to the provided configuration."""

    normalized_config = config.normalized()
    result = OrganizationResult()

    if not normalized_config.input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {config.input_dir}")

    validate_directories(
        input_dir=normalized_config.input_dir,
        output_dir=normalized_config.output_dir,
    )

    media_items = collect_supported_items(normalized_config, result)
    reserved_paths: set[Path] = set()

    for group in group_items_by_checksum(media_items):
        for index, item in enumerate(order_duplicate_group(group)):
            duplicate = index > 0

            try:
                desired_destination, manual_review = build_desired_destination(
                    normalized_config.output_dir,
                    item.metadata,
                    duplicate=duplicate,
                )
                destination, already_exists = next_available_path(
                    desired_destination,
                    checksum=item.checksum,
                    reserved_paths=reserved_paths,
                )
                reserved_paths.add(destination)

                if not already_exists:
                    copy_media_file(
                        item.path,
                        destination,
                        dry_run=normalized_config.dry_run,
                    )

                status = "already exists" if already_exists else "planned"
                if not normalized_config.dry_run and not already_exists:
                    status = "copied"

                action = f"{status}: {item.path} -> {destination}"
                result.actions.append(action)
                logger.info("%s", action)

                record_result(
                    result,
                    manual_review=manual_review,
                    duplicate=duplicate,
                    already_exists=already_exists,
                )

            except Exception as exc:
                result.errors += 1
                logger.exception("Failed to process %s: %s", item.path, exc)

    return result
