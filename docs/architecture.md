# Architecture

The project is organized around a small command-line workflow.

## Flow

```text
input directory
  -> recursive file scan
  -> media type detection
  -> metadata and file-name date collection
  -> checksum grouping
  -> canonical file selection
  -> trusted date selection by source priority
  -> destination planning
  -> copy or mark as already existing
```

## Modules

- `config`: runtime settings for input, output, supported extensions, and dry-run mode.
- `metadata`: file extension detection, EXIF extraction, optional Windows video metadata, file-name parsing, and date candidate priority.
- `naming`: trusted date selection by source priority and output name formatting.
- `duplicates`: SHA3 checksum calculation.
- `organizer`: orchestration of scanning, routing, copying, and result counters.
- `cli`: command-line interface.

## Data Handling

The tool copies files instead of moving them. This keeps the original archive unchanged and makes the workflow safer for personal media.

Files with no trusted date are routed to `to_check/` rather than being forced into a guessed location. File modification time is collected, but it is not treated as reliable enough for automatic organization by itself.

If an expected destination already exists with the same checksum, the file is counted as already existing instead of creating a numbered copy.

## Output Categories

- Regular organized files: `output/YYYY/MM/DD/`
- Duplicates after canonical selection: `output/repeated/YYYY/MM/DD/`
- Files that require manual review: `output/to_check/`
