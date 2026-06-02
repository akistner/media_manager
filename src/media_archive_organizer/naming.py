"""Naming rules for organized media files."""

from __future__ import annotations

from datetime import datetime

from media_archive_organizer.metadata import DateCandidate, MediaMetadata

MIN_VALID_YEAR = 2000


def choose_trusted_candidate(
    candidates: tuple[DateCandidate, ...],
) -> DateCandidate | None:
    """Choose the best trusted date candidate from year 2000 onward."""

    trusted_candidates = [
        candidate
        for candidate in candidates
        if candidate.trusted and candidate.value.year >= MIN_VALID_YEAR
    ]

    if not trusted_candidates:
        return None

    precision_rank = {"datetime": 0, "date": 1}

    return min(
        trusted_candidates,
        key=lambda candidate: (
            candidate.priority,
            precision_rank[candidate.precision],
            candidate.value,
        ),
    )


def choose_trusted_date(candidates: tuple[DateCandidate, ...]) -> datetime | None:
    """Choose the best trusted date value from year 2000 onward."""

    candidate = choose_trusted_candidate(candidates)
    return candidate.value if candidate else None


def build_media_stem(media_metadata: MediaMetadata, selected_date: datetime) -> str:
    """Build the organized file stem for a media item."""

    prefix = "img" if media_metadata.media_type == "image" else "vid"
    date_part = selected_date.strftime("%Y%m%d")
    time_part = selected_date.strftime("%H%M%S")

    if time_part == "000000":
        return f"{prefix}_{date_part}"

    return f"{prefix}_{date_part}_{time_part}"
