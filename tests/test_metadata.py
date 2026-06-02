from datetime import datetime
from pathlib import Path

from media_archive_organizer.metadata import (
    parse_date_candidate_from_name,
    parse_datetime_from_name,
)


def test_parse_datetime_from_common_camera_name() -> None:
    result = parse_datetime_from_name(Path("P_20161215_190101_BF.jpg"))

    assert result == datetime(2016, 12, 15, 19, 1, 1)


def test_parse_datetime_from_dash_and_dot_name() -> None:
    result = parse_datetime_from_name(Path("2013-09-06 16.06.06.jpg"))

    assert result == datetime(2013, 9, 6, 16, 6, 6)


def test_parse_date_only_from_messaging_app_name() -> None:
    result = parse_datetime_from_name(Path("IMG-20161030-WA0031.jpeg"))

    assert result == datetime(2016, 10, 30)


def test_parse_date_candidate_marks_file_name_date_precision() -> None:
    result = parse_date_candidate_from_name(Path("IMG-20161030-WA0031.jpeg"))

    assert result is not None
    assert result.source == "file_name_date"
    assert result.precision == "date"


def test_parse_date_candidate_marks_file_name_datetime_precision() -> None:
    result = parse_date_candidate_from_name(Path("P_20161215_190101_BF.jpg"))

    assert result is not None
    assert result.source == "file_name_datetime"
    assert result.precision == "datetime"


def test_parse_datetime_returns_none_when_name_has_no_date() -> None:
    result = parse_datetime_from_name(Path("holiday-photo.jpg"))

    assert result is None


def test_parse_datetime_returns_none_when_name_has_invalid_date() -> None:
    result = parse_datetime_from_name(Path("IMG-20221315-WA0001.jpg"))

    assert result is None
