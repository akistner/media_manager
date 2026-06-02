import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def workspace_tmp(request: pytest.FixtureRequest) -> Iterator[Path]:
    """Create a test directory inside the repository workspace."""

    safe_name = request.node.name.replace("/", "_").replace("\\", "_")
    root = Path(__file__).parent / ".runtime_tmp" / safe_name

    if root.exists():
        shutil.rmtree(root)

    root.mkdir(parents=True)

    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)

