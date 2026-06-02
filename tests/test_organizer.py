import pytest

from media_archive_organizer.config import OrganizerConfig
from media_archive_organizer.organizer import organize_media


def test_organize_media_routes_files_by_date_duplicate_and_review(
    workspace_tmp,
) -> None:
    input_dir = workspace_tmp / "input"
    output_dir = workspace_tmp / "output"
    input_dir.mkdir()

    original = input_dir / "P_20161215_190101_BF.jpg"
    duplicate = input_dir / "P_20161215_190101_BF - Copy.jpg"
    uncertain = input_dir / "holiday-photo.jpg"
    unsupported = input_dir / "notes.txt"

    original.write_bytes(b"same image content")
    duplicate.write_bytes(b"same image content")
    uncertain.write_bytes(b"no date in this file name")
    unsupported.write_text("not media", encoding="utf-8")

    result = organize_media(
        OrganizerConfig(input_dir=input_dir, output_dir=output_dir)
    )

    assert result.scanned == 4
    assert result.organized == 1
    assert result.repeated == 1
    assert result.to_check == 1
    assert result.skipped == 1
    assert result.errors == 0

    assert (output_dir / "2016" / "12" / "15" / "img_20161215_190101.jpg").exists()
    assert (
        output_dir
        / "repeated"
        / "2016"
        / "12"
        / "15"
        / "img_20161215_190101.jpg"
    ).exists()
    assert (output_dir / "to_check" / "holiday-photo.jpg").exists()

    original_action = next(
        action for action in result.actions if str(original) in action
    )
    duplicate_action = next(
        action for action in result.actions if str(duplicate) in action
    )

    assert str(output_dir / "repeated") not in original_action
    assert str(output_dir / "repeated") in duplicate_action


def test_dry_run_does_not_copy_files(workspace_tmp) -> None:
    input_dir = workspace_tmp / "input"
    output_dir = workspace_tmp / "output"
    input_dir.mkdir()

    (input_dir / "P_20161215_190101_BF.jpg").write_bytes(b"content")

    result = organize_media(
        OrganizerConfig(input_dir=input_dir, output_dir=output_dir, dry_run=True)
    )

    assert result.organized == 1
    assert result.actions
    assert not output_dir.exists()


def test_second_run_does_not_create_numbered_copies(workspace_tmp) -> None:
    input_dir = workspace_tmp / "input"
    output_dir = workspace_tmp / "output"
    input_dir.mkdir()

    (input_dir / "P_20161215_190101_BF.jpg").write_bytes(b"same image content")
    (input_dir / "P_20161215_190101_BF - Copy.jpg").write_bytes(
        b"same image content"
    )
    (input_dir / "holiday-photo.jpg").write_bytes(b"no date in this file name")

    organize_media(OrganizerConfig(input_dir=input_dir, output_dir=output_dir))
    second_result = organize_media(
        OrganizerConfig(input_dir=input_dir, output_dir=output_dir)
    )

    assert second_result.already_exists == 3
    assert second_result.organized == 0
    assert second_result.repeated == 0
    assert second_result.to_check == 0
    assert not list(output_dir.rglob("*_02.*"))


def test_output_directory_cannot_be_inside_input_directory(workspace_tmp) -> None:
    input_dir = workspace_tmp / "input"
    output_dir = input_dir / "output"
    input_dir.mkdir()

    with pytest.raises(ValueError, match="inside the input directory"):
        organize_media(OrganizerConfig(input_dir=input_dir, output_dir=output_dir))
