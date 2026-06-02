"""Duplicate detection based on file checksums."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path


def calculate_checksum(path: Path, block_size: int = 65536) -> str:
    """Calculate a SHA3-256 checksum for a file."""

    digest = hashlib.sha3_256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            digest.update(block)

    return digest.hexdigest()


@dataclass
class ChecksumRegistry:
    """Track checksums seen during one organization run."""

    checksums: dict[str, Path] = field(default_factory=dict)

    def is_duplicate(self, path: Path) -> bool:
        """Return true when the file checksum was already seen."""

        checksum = calculate_checksum(path)

        if checksum in self.checksums:
            return True

        self.checksums[checksum] = path
        return False

