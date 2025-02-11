# Gopro-files-rename-utility
A Python script that renames Gopro files


This Python script converts GoPro's default naming format (e.g., GH011440.MP4) to a more intuitive format (e.g, 1440_1.MP4), which maintains chronological order of video parts. It creates renamed files in a new directory, and never modifies original files.

Here is an example of what video filenames might look like with a GoPro. They are listed here in chronological order:
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
GH011449.MP4 -> 1449_1.MP4
GH021447.MP4 -> 1447_2.MP4
GH021449.MP4 -> 1449_2.MP4
GH031449.MP4 -> 1449_3.MP4
```

## Usage
### Basic File Renaming
```bash
python gopro_utility.py --input /path/to/videos
```

It also supports video merging using FFmpeg using `--merge`
```bash
python gopro_utility.py --input /path/to/videos --merge
```
Files are combined using FFmpeg's stream copy, maintaining original quality


## Requirements
tqdm for process bar
```bash
pip install tqdm
```

FFmpeg Installation
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS (Homebrew): `brew install ffmpeg`
- Windows: Download from FFmpeg website or use Chocolatey: `choco install ffmpeg`

