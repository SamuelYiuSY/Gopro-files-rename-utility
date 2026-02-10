# GoPro Video Processor

A Python utility to organize, rename, and optionally merge GoPro video files.

## Overview

This Python script converts GoPro's default naming format (e.g., GH011440.MP4) to a more intuitive format (e.g, 1440_1.MP4), which maintains chronological order of video parts. It creates renamed files in a new directory, and never modifies original files.

Here is an example of what GoPro original video filenames look like. They are listed here in chronological order:
```
GH011440.MP4 = video 1440 start
GH011447.MP4 = video 1447 start
GH011449.MP4 = video 1449 start
GH021447.MP4 = video 1449 continued
GH021449.MP4 = video 1447 continued
GH031449.MP4 = video 1449 last part
```

The same files after running the script should look like this:
```
GH011440.MP4 -> 1440_1.MP4
GH011447.MP4 -> 1447_1.MP4
GH021447.MP4 -> 1447_2.MP4
GH011449.MP4 -> 1449_1.MP4
GH021449.MP4 -> 1449_2.MP4
GH031449.MP4 -> 1449_3.MP4
```

or this with `--merge` flag:
```
GH011440.MP4 -> 1440.MP4
GH011447.MP4 + GH021447.MP4 -> 1447.MP4
GH011449.MP4 + GH021449.MP4 + GH031449.MP4 -> 1449.MP4
```

## Usage
### Basic File Renaming
```bash
python gopro_utility.py --input /path/to/videos
```

It also supports video merging using FFmpeg using `--merge` or `-m`
```bash
python gopro_utility.py --input /path/to/videos --merge
```

**Arguments:**

- `--input, -i` — Input directory containing GoPro files (default: current directory `.`)
- `--merge, -m` — Flag to merge video parts into single files (default: off)

Files are combined using FFmpeg's stream copy, maintaining original quality


### Examples

**Rename files only (no merging):**
```bash
python script.py --input ./gopro_videos
```

**Merge video parts:**
```bash
python script.py --input ./gopro_videos --merge
```

## Installation

### Requirements
- Python 3.6+
- ffmpeg (with ffprobe)
- tqdm (`pip install tqdm`)

### Setup

```bash
pip install tqdm
```

Ensure ffmpeg and ffprobe are installed and available in your system PATH.

## Output

All processed files are saved to a `processed_videos/` directory created in the input directory. Original files are not modified.

## How It Works

1. **File Detection** — Scans directory for GoPro files (starting with `GH` and ending with `.MP4`)
2. **Grouping** — Groups files by video number (characters 4-8 in filename)
3. **Sorting** — Sorts parts by part number (characters 2-4 in filename)
4. **Processing** — Either renames files or merges them using ffmpeg's concat demuxer
5. **Progress Tracking** — Shows progress bar during merging operations

## Notes

- Files are processed without re-encoding (fast operation)
- Original files remain untouched
- Merged videos use `+faststart` flag for optimized web playback
- Progress bar is only shown during merge operations (requires total video duration)
