"""Metadata extraction for local media files."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from re import Pattern
from typing import Literal

logger = logging.getLogger(__name__)

MediaType = Literal["image", "video", "unsupported"]
DatePrecision = Literal["date", "datetime"]

DATE_SOURCE_PRIORITIES = {
    "exif_original": 10,
    "windows_video_encoded": 20,
    "exif_digitized": 30,
    "exif_datetime": 40,
    "file_name_datetime": 50,
    "file_name_date": 60,
    "file_modified": 90,
}


@dataclass(frozen=True)
class DateCandidate:
    """A possible date collected from a media file.

    Parameters:
        source: Human-readable source name, such as ``exif_original``.
        value: Parsed date and time.
        trusted: Whether this source is reliable enough for automatic organization.
        precision: Whether the value represents a date or a full datetime.
        priority: Source priority used when choosing the organized file date.
    """

    source: str
    value: datetime
    trusted: bool
    precision: DatePrecision = "datetime"
    priority: int = 100


@dataclass(frozen=True)
class MediaMetadata:
    """Metadata collected for one media file."""

    path: Path
    extension: str
    media_type: MediaType
    date_candidates: tuple[DateCandidate, ...] = field(default_factory=tuple)


FILENAME_PATTERNS: tuple[Pattern[str], ...] = (
    re.compile(r"(?<!\d)(?P<date>\d{8})[-_](?P<time>\d{6})(?!\d)"),
    re.compile(
        r"(?<!\d)(?P<date>\d{4}-\d{2}-\d{2})\s*at\s*"
        r"(?P<time>\d{2}[._-]\d{2}[._-]\d{2})(?!\d)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?<!\d)(?P<date>\d{4}-\d{2}-\d{2})\s+"
        r"(?P<time>\d{2}[._-]\d{2}[._-]\d{2})(?!\d)",
    ),
    re.compile(r"(?<!\d)(?P<date>\d{8})_(?P<time>\d{2}_\d{2}_\d{2})(?!\d)"),
    re.compile(r"(?<!\d)(?P<date>\d{8})(?!\d)"),
)


def build_date_candidate(
    source: str,
    value: datetime,
    trusted: bool,
    precision: DatePrecision = "datetime",
) -> DateCandidate:
    """Build a date candidate with the configured source priority."""

    return DateCandidate(
        source=source,
        value=value,
        trusted=trusted,
        precision=precision,
        priority=DATE_SOURCE_PRIORITIES.get(source, 100),
    )


def get_extension(path: Path) -> str:
    """Return the file extension without a leading dot."""

    return path.suffix.lower().lstrip(".")


def get_media_type(
    extension: str,
    image_extensions: tuple[str, ...],
    video_extensions: tuple[str, ...],
) -> MediaType:
    """Classify a file extension as image, video, or unsupported."""

    if extension in image_extensions:
        return "image"
    if extension in video_extensions:
        return "video"
    return "unsupported"


def parse_date_candidate_from_name(path: Path) -> DateCandidate | None:
    """Parse a trusted date candidate from a media file name.

    Supported examples include ``P_20161215_190101_BF.jpg``,
    ``2013-09-06 16.06.06.jpg``, and ``IMG-20161030-WA0031.jpeg``.
    """

    for pattern in FILENAME_PATTERNS:
        match = pattern.search(path.name)
        if not match:
            continue

        date_part = re.sub(r"[^0-9]", "", match.group("date"))
        time_part = match.groupdict().get("time")

        if time_part:
            digits = re.sub(r"[^0-9]", "", time_part)
            try:
                parsed = datetime.strptime(f"{date_part} {digits}", "%Y%m%d %H%M%S")
            except ValueError:
                logger.debug("Skipped invalid date in file name: %s", path.name)
                continue

            return build_date_candidate(
                source="file_name_datetime",
                value=parsed,
                trusted=True,
                precision="datetime",
            )

        try:
            parsed = datetime.strptime(date_part, "%Y%m%d")
        except ValueError:
            logger.debug("Skipped invalid date in file name: %s", path.name)
            continue

        return build_date_candidate(
            source="file_name_date",
            value=parsed,
            trusted=True,
            precision="date",
        )

    return None


def parse_datetime_from_name(path: Path) -> datetime | None:
    """Parse a date or datetime value from a media file name."""

    candidate = parse_date_candidate_from_name(path)
    return candidate.value if candidate else None


def extract_image_dates(path: Path) -> list[DateCandidate]:
    """Extract EXIF date candidates from an image.

    The function returns an empty list when Pillow is unavailable, the file cannot
    be opened as an image, or the image has no relevant EXIF dates.
    """

    try:
        from PIL import ExifTags, Image
    except ImportError:
        logger.debug("Pillow is not installed; image EXIF dates were skipped.")
        return []

    date_tags = {
        "DateTime": "exif_datetime",
        "DateTimeOriginal": "exif_original",
        "DateTimeDigitized": "exif_digitized",
    }
    candidates: list[DateCandidate] = []

    try:
        with Image.open(path) as image:
            exif_data = image.getexif()

        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            source = date_tags.get(tag_name)
            if source is None:
                continue

            try:
                parsed = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
            except ValueError:
                logger.debug("Skipped invalid EXIF date %r in %s.", value, path.name)
                continue

            candidates.append(
                build_date_candidate(source=source, value=parsed, trusted=True)
            )

    except OSError:
        logger.debug("Could not read image metadata from %s.", path.name)

    return candidates


def extract_windows_video_date(path: Path) -> DateCandidate | None:
    """Extract the Windows media encoded date for a video file when available."""

    try:
        from win32com.propsys import propsys, pscon
    except ImportError:
        logger.debug("pywin32 is not installed; Windows video dates were skipped.")
        return None

    try:
        properties = propsys.SHGetPropertyStoreFromParsingName(str(path))
        raw_value = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
    except Exception as exc:
        logger.debug(
            "Could not read Windows video metadata from %s: %s",
            path.name,
            exc,
        )
        return None

    if raw_value is None:
        return None

    raw_text = str(raw_value)[:19]
    try:
        parsed = datetime.strptime(raw_text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.debug(
            "Skipped invalid Windows video date %r in %s.",
            raw_value,
            path.name,
        )
        return None

    return build_date_candidate(
        source="windows_video_encoded",
        value=parsed,
        trusted=True,
    )


def collect_metadata(
    path: Path,
    image_extensions: tuple[str, ...],
    video_extensions: tuple[str, ...],
) -> MediaMetadata:
    """Collect metadata candidates for one file."""

    extension = get_extension(path)
    media_type = get_media_type(extension, image_extensions, video_extensions)
    candidates: list[DateCandidate] = []

    if media_type == "unsupported":
        return MediaMetadata(path=path, extension=extension, media_type=media_type)

    if media_type == "image":
        candidates.extend(extract_image_dates(path))
    elif media_type == "video":
        video_date = extract_windows_video_date(path)
        if video_date is not None:
            candidates.append(video_date)

    name_date = parse_date_candidate_from_name(path)
    if name_date is not None:
        candidates.append(name_date)

    modified_date = datetime.fromtimestamp(path.stat().st_mtime)
    candidates.append(
        build_date_candidate(
            source="file_modified",
            value=modified_date,
            trusted=False,
        )
    )

    return MediaMetadata(
        path=path,
        extension=extension,
        media_type=media_type,
        date_candidates=tuple(candidates),
    )
