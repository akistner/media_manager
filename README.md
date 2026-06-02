# Personal Media Archive Organizer

Personal Media Archive Organizer is a Python tool for organizing a local photo and video archive. It reads dates from file names, image EXIF metadata, optional Windows video metadata, and file modification time, then copies files into a date-based folder structure.

This public version is designed for safe portfolio use. It uses synthetic sample files and does not require real personal media to understand or test the project.

## What It Does

- Scans an input directory recursively.
- Detects supported image and video files.
- Extracts possible dates from metadata and file names.
- Chooses a reliable date for the organized file name.
- Copies files into `year/month/day` folders.
- Sends files with uncertain dates to `to_check/`.
- Detects duplicate files using a SHA3 checksum.
- Chooses a canonical file before routing duplicates.
- Skips copying when the same file already exists at the target path.
- Keeps existing output files unchanged when resolving naming conflicts.

## Why This Project Exists

Personal media archives often contain files from phones, messaging apps, cloud backups, and old folders. File names and metadata are inconsistent, and manual organization becomes slow and error-prone.

This project automates the repetitive parts while keeping uncertain files visible for manual review.

## Project Structure

```text
.
├── README.md
├── pyproject.toml
├── .env.example
├── src/
│   └── media_archive_organizer/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── duplicates.py
│       ├── logging_config.py
│       ├── metadata.py
│       ├── naming.py
│       └── organizer.py
├── tests/
├── data/
│   └── sample/
└── docs/
    ├── architecture.md
    ├── decisions.md
    └── evidence_pack_private.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

On Windows, `pywin32` is used when available to read video encoded dates from file properties. The organizer still works without it, but video dates may depend on file names or modification time.

## Usage

Run with explicit input and output folders:

```bash
media-organizer --input-dir data/sample/input --output-dir data/sample/output
```

Preview actions without copying files:

```bash
media-organizer --input-dir data/sample/input --output-dir data/sample/output --dry-run
```

You can also run the module directly:

```bash
python -m media_archive_organizer --input-dir data/sample/input --output-dir data/sample/output
```

## Date Selection Rules

The organizer treats dates from EXIF, video encoded metadata, and file names as trusted sources. File modification time is collected as a fallback reference, but a file with only modification time is sent to `to_check/` because modification dates can be changed by downloads, copies, or cloud sync.

When multiple trusted dates are available, the organizer uses source priority before comparing dates. For example, a full EXIF original timestamp is preferred over a file-name date that only contains the day.

## Output Layout

Organized files:

```text
output/
└── 2016/
    └── 12/
        └── 15/
            └── img_20161215_190101.jpg
```

Duplicate files:

```text
output/
└── repeated/
    └── 2016/
        └── 12/
            └── 15/
                └── img_20161215_190101.jpg
```

Files without a trusted date:

```text
output/
└── to_check/
    └── holiday_photo.jpg
```

## Testing

Run the test suite:

```bash
pytest
```

Run static checks:

```bash
ruff check .
```

## Privacy Notes

Do not commit real photos, videos, generated outputs, or private Evidence Pack files. Real media can contain personal data, location data, device information, and private timestamps.

Use `data/sample/` only for synthetic or anonymized files.

## Limitations

- Duplicate detection uses the input files from the current run and existing output files at the expected target path.
- HEIC/HEIF support depends on the local Pillow installation and available codecs.
- Windows video metadata is optional and requires `pywin32`.
- Files with only modification dates are intentionally sent to manual review.
- This tool copies files instead of moving them to reduce the risk of accidental data loss.
