# Design Decisions

## Copy Instead of Move

The organizer copies files to the output directory and leaves the input files untouched. This is safer for a personal archive because the original source remains available if a rule needs to be adjusted.

## CLI First

The original version included a small Flask endpoint. The improved version uses a command-line interface as the main entry point because the task is local, file-based, and normally run by one person. A web API can be added later if there is a real need for remote triggering.

## Treat File Modification Time as Weak Evidence

File modification time can be changed by copying, downloading, cloud synchronization, or manual edits. The tool records it as a candidate but does not use it as the only reason to organize a file automatically.

## Prefer Higher-Quality Date Sources

When several trusted dates are available, the organizer does not simply pick the earliest value. It prefers higher-quality sources first, such as EXIF original timestamps, then falls back to lower-confidence sources such as dates parsed from file names.

## Do Not Rename Existing Output Files

When a naming conflict happens, the incoming file receives a numeric suffix. Existing output files are not renamed. This avoids surprising changes to files that were already organized.

## Avoid Re-Copying Existing Files

If the expected destination already exists and has the same checksum as the input file, the organizer counts it as already existing. This keeps repeated runs from producing `_02`, `_03`, and similar copies for the same content.

## Choose a Canonical File Before Routing Duplicates

Files with the same checksum are grouped before copying. The organizer prefers a representative file whose name does not look like an explicit copy, then sends the remaining files to `repeated/`.
