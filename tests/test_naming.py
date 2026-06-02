from datetime import datetime
from pathlib import Path

from media_archive_organizer.metadata import (
    DateCandidate,
    MediaMetadata,
    build_date_candidate,
)
from media_archive_organizer.naming import build_media_stem, choose_trusted_date


def test_choose_trusted_date_ignores_file_modified_only() -> None:
    candidates = (
        DateCandidate(
            source="file_modified",
            value=datetime(2026, 1, 1, 9, 0, 0),
            trusted=False,
        ),
    )

    assert choose_trusted_date(candidates) is None


def test_choose_trusted_date_returns_earliest_trusted_date() -> None:
    candidates = (
        DateCandidate(
            source="file_name",
            value=datetime(2016, 12, 15, 19, 1, 1),
            trusted=True,
        ),
        DateCandidate(
            source="exif_original",
            value=datetime(2016, 12, 15, 19, 0, 0),
            trusted=True,
        ),
    )

    assert choose_trusted_date(candidates) == datetime(2016, 12, 15, 19, 0, 0)


def test_choose_trusted_date_prefers_source_priority_over_earliest_date() -> None:
    candidates = (
        build_date_candidate(
            source="file_name_date",
            value=datetime(2016, 10, 30),
            trusted=True,
            precision="date",
        ),
        build_date_candidate(
            source="exif_original",
            value=datetime(2016, 10, 30, 10, 53, 16),
            trusted=True,
        ),
    )

    assert choose_trusted_date(candidates) == datetime(2016, 10, 30, 10, 53, 16)


def test_build_media_stem_omits_midnight_time() -> None:
    metadata = MediaMetadata(
        path=Path("IMG-20161030-WA0031.jpg"),
        extension="jpg",
        media_type="image",
    )

    assert build_media_stem(metadata, datetime(2016, 10, 30)) == "img_20161030"


def test_build_media_stem_keeps_non_midnight_time() -> None:
    metadata = MediaMetadata(
        path=Path("VID_20161215_190101.mp4"),
        extension="mp4",
        media_type="video",
    )

    assert (
        build_media_stem(metadata, datetime(2016, 12, 15, 19, 1, 1))
        == "vid_20161215_190101"
    )
