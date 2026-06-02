"""Configuration objects for the media archive organizer."""

from dataclasses import dataclass
from pathlib import Path

DEFAULT_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "heic", "heif")
DEFAULT_VIDEO_EXTENSIONS = ("mp4", "3gp", "mov")


@dataclass(frozen=True)
class OrganizerConfig:
    """Runtime configuration for one organization run.

    Parameters:
        input_dir: Directory containing media files to scan recursively.
        output_dir: Directory where organized copies are written.
        dry_run: When true, plan actions without copying files.
        image_extensions: Supported image extensions without leading dots.
        video_extensions: Supported video extensions without leading dots.
    """

    input_dir: Path
    output_dir: Path
    dry_run: bool = False
    image_extensions: tuple[str, ...] = DEFAULT_IMAGE_EXTENSIONS
    video_extensions: tuple[str, ...] = DEFAULT_VIDEO_EXTENSIONS

    def normalized(self) -> "OrganizerConfig":
        """Return a copy with resolved directory paths and normalized extensions."""

        return OrganizerConfig(
            input_dir=self.input_dir.expanduser().resolve(),
            output_dir=self.output_dir.expanduser().resolve(),
            dry_run=self.dry_run,
            image_extensions=tuple(
                ext.lower().lstrip(".") for ext in self.image_extensions
            ),
            video_extensions=tuple(
                ext.lower().lstrip(".") for ext in self.video_extensions
            ),
        )
