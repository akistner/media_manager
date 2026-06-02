from media_archive_organizer.duplicates import ChecksumRegistry


def test_checksum_registry_detects_duplicates(workspace_tmp) -> None:
    first = workspace_tmp / "first.jpg"
    second = workspace_tmp / "second.jpg"
    different = workspace_tmp / "different.jpg"

    first.write_bytes(b"same content")
    second.write_bytes(b"same content")
    different.write_bytes(b"different content")

    registry = ChecksumRegistry()

    assert registry.is_duplicate(first) is False
    assert registry.is_duplicate(second) is True
    assert registry.is_duplicate(different) is False
