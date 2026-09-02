# ffmpeg-helper-tools

Python scripts for batch video processing with ffmpeg. Each script walks a directory recursively, detects video files using ffprobe.

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/vherolf/ffmpeg-helper-tools/main/install.sh | bash
```

Run the same command again at any time to update.

The script checks for system dependencies (`python3`, `pip3`, `ffmpeg`, `ffprobe`, `git`, and — non-blocking — `libmagic`), clones or pulls the repo into `./ffmpeg-helper-tools` (relative to where you run the command), creates a venv, and installs all packages.

### System dependencies

**Ubuntu / Debian:** `sudo apt install -y git python3 python3-pip python3-venv ffmpeg`

**macOS:** `brew install git python3 ffmpeg`

`archiver.py` additionally needs `libmagic1` (Ubuntu/Debian) / `libmagic` (macOS) — the installer checks for it and warns if missing, but won't block the rest of the install.

### Build standalone binaries

After installing, run:

```bash
./build.sh
```

This uses PyInstaller to compile each script into a self-contained binary in `dist/`. The binaries have no Python dependency — copy them anywhere and run directly:

```bash
./dist/compressor -s /videos -d /output
./dist/resizer -r 1080 -n
```

`ffmpeg` and `ffprobe` still need to be installed on the system.

---

### Manual install

```bash
git clone https://github.com/vherolf/ffmpeg-helper-tools.git
cd ffmpeg-helper-tools
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Scripts

### analyzer.py

Prints the path, resolution, codec, and duration for every video found.

```bash
python analyzer.py
python analyzer.py -d /path/to/videos
python analyzer.py -l                    # also log to ./analyzer.log
```

---

### compressor.py

Re-encodes videos to H.265 (libx265) at CRF 28.

```bash
python compressor.py
python compressor.py -s /path/to/videos -d /path/to/output
python compressor.py -c 23               # lower CRF = higher quality (range 0–51)
python compressor.py -n                  # dry run — print actions without encoding
python compressor.py -l                  # also log to <destination>/compressor.log
python compressor.py -l /path/to/file.log  # or log to a specific file
```

Defaults: source = current directory, destination = `~/Desktop/compressed_videos`, CRF = 28.

---

### resizer.py

Resizes videos to 720p height while preserving aspect ratio.

```bash
python resizer.py
python resizer.py -s /path/to/videos -d /path/to/output
python resizer.py -r 1080                # resize to 1080p instead
python resizer.py -c 23                  # lower CRF = higher quality (range 0–51)
python resizer.py -n                     # dry run — print actions without resizing
```

Defaults: source = current directory, destination = `~/Desktop/resized_videos`, resolution = 720, CRF = 28.

---

### renamer.py

Copies videos with spaces in filenames replaced by underscores. The original file extension/container is preserved (this is a plain copy, not a transcode).

```bash
python renamer.py
python renamer.py -s /path/to/videos -d /path/to/output
python renamer.py -n                      # dry run — print actions without copying
python renamer.py -l                      # also log to <destination>/renamer.log
```

Defaults: source = current directory, destination = `~/Desktop/renamed_videos`.

---

### mosaic.py

Merges pairs of videos found in the same folder side-by-side (default) or stacked vertically. Output goes to the current directory by default.

```bash
python mosaic.py                  # horizontal (side-by-side)
python mosaic.py -v               # vertical (stacked)
python mosaic.py -s /path/to/videos
python mosaic.py -s /path/to/videos -d /path/to/output
python mosaic.py -c 23            # lower CRF = higher quality (range 0–51)
python mosaic.py -n               # dry run — print actions without merging
python mosaic.py -l               # also log to <destination>/mosaic.log
```

Each subfolder must contain exactly 2 video files (others are skipped with a warning).

---

### mosaic-left-right.py

Like `mosaic.py` but uses `_left` / `_right` in filenames to determine order. The output filename is derived by stripping the `_left` / `_right` suffix.

```bash
python mosaic-left-right.py
python mosaic-left-right.py -d /path/to/videos
python mosaic-left-right.py -v          # vertical (stacked)
python mosaic-left-right.py -c 23       # lower CRF = higher quality (range 0–51)
python mosaic-left-right.py -n          # dry run — print actions without merging
python mosaic-left-right.py -l          # also log to <output>/mosaic-left-right.log
```

Output always goes to `~/Desktop/merged_videos` (no destination override). Each subfolder must contain exactly 2 video files, and their filenames must end in `_left`/`_right` (others are skipped with a warning).

---

### videoslicer-horizontal.py

Splits a wide video into 3 equal horizontal scenes using ffmpeg's crop filter.
A video at 5760x1080 produces three 1920x1080 clips.

```bash
python videoslicer-horizontal.py
python videoslicer-horizontal.py -s /path/to/videos -d /path/to/output
python videoslicer-horizontal.py -c 23   # lower CRF = higher quality (range 0–51)
python videoslicer-horizontal.py -n      # dry run — print actions without slicing
python videoslicer-horizontal.py -l      # also log to <destination>/videoslicer-horizontal.log
```

Filenames must follow the format `YYYY-MM-DD HH-MM-SS.ext` (e.g. `2022-05-24 15-46-07.mkv`) — files that don't match are skipped with an error.
Output is written to `<destination>/<date>/<time>/`. Defaults: source = current directory, destination = `~/Desktop/sliced_videos`, CRF = 28.

---

### videoslicer-vertical.py

Splits a video into 2 equal vertical scenes using ffmpeg's crop filter.
A video at 1920x1080 produces two 960x540 clips.

```bash
python videoslicer-vertical.py
python videoslicer-vertical.py -s /path/to/videos -d /path/to/output
python videoslicer-vertical.py -c 23     # lower CRF = higher quality (range 0–51)
python videoslicer-vertical.py -n        # dry run — print actions without slicing
python videoslicer-vertical.py -l        # also log to <destination>/videoslicer-vertical.log
```

Same filename format requirement as `videoslicer-horizontal.py` (non-matching files are skipped with an error). Defaults: source = current directory, destination = `~/Desktop/sliced_videos`, CRF = 28.

---

### generate-test-media.py

Generates numbered test images (using Pillow) and converts them to videos — useful for testing the other scripts.

```bash
python generate-test-media.py            # generate images + videos
python generate-test-media.py -l         # list available fonts
python generate-test-media.py -c 23      # lower CRF = higher quality (range 0–51)
```

Output is written to `videos/`, `images/`, and `videos_merge/` in the current directory.

---

### archiver.py

Archives a project folder to a new location: non-video files are copied as-is, video files are re-encoded to H.265, and the original directory structure is preserved. The source folder name is always kept under the destination (e.g. `-d ~/Desktop/archive` with a source named `tet` writes to `~/Desktop/archive/tet/`).

```bash
python archiver.py -s /path/to/project -d /path/to/archive
python archiver.py -s /path/to/project -d /path/to/archive -c 23   # lower CRF = higher quality (range 0–51)
python archiver.py -s /path/to/project -d /path/to/archive -n     # dry run — print actions without writing
python archiver.py -s /path/to/project -d /path/to/archive -l     # also log to <destination>/<project>/archiver.log
```

`-s/--source_directory` and `-d/--destination_directory` are required — this script can move a lot of data, so the paths are never defaulted. Default CRF = 28. Videos are always re-encoded (never just remuxed), even if already H.265 — codec alone doesn't guarantee the source is already small.

Video detection here is two-layered: a fast `libmagic` MIME check first, falling back to the same ffprobe-based check the rest of the suite uses (`common.is_video`) for formats libmagic misidentifies (AVCHD `.mts`/`.m2ts`, MPEG-TS, VOB, etc.). Needs `libmagic1`/`libmagic` installed — see System dependencies above.

After each video is compressed, its output duration is compared against the source (via ffprobe) — a mismatch beyond a small tolerance is treated as a failed/truncated encode and reported as an error rather than a false "done". Compressed videos also keep the source file's original timestamp (`shutil.copystat`), so the archived copy still reflects when it was actually recorded, not when it was archived.

Prints a per-file `[VIDEO]`/`[COPY]`/`[ERROR]` line as it goes, then a final count and a source-vs-destination size comparison.

---

## common.py

Shared helpers used by every script:

- `is_video(filename)` — runs ffprobe on the file and returns `True` if it contains a video stream, excluding still images (PNG/JPEG/GIF etc., which ffprobe also reports a "video" stream for). Format-agnostic, works on any container.
- `iter_files(source)` / `iter_videos(source)` — generators that walk `source` recursively and yield `(root, file)` tuples; `iter_videos` filters to files where `is_video` is true. Used by every script instead of a hand-rolled `os.walk` loop.
- `get_logger(name)` / `add_file_handler(logger, path)` — a console logger every script uses by default, plus an opt-in file handler wired up behind each script's `-l/--log-file` flag.

---

# FFMPEG Cheatsheet

## convert videos
```ffmpeg -i input.MTS output.mp4```  

## compress videos
crf is 0-51 (23-28 is a good choice)  
compress the videos with ffmpeg to h.265 (better)  
```ffmpeg -i videoin.mp4 -vcodec libx265 -crf 28 -c:a copy videoout.mp4 -y```  
compress the videos with ffmpeg to h.264 (for legacy systems)  
```ffmpeg -i input.MTS -crf 23 output.mp4```  

## concat videos
```ffmpeg -i "concat:00008.MTS|00009.MTS|00021.MTS|00010.MTS" -crf 23  output.mp4```

## cut out part of video
https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg

```ffmpeg -i input.mp4 -filter:v crop=iw/2:ih/2:0:0 -c:a copy output.mp4```


## trim a video
- The -ss parameter is the starting point.
- The -t provides the length of the clip  
```ffmpeg -i input.mp4 -ss 00:00:10 -t 00:20:00 -async 1 output.mp4```

## make animated gif from mp4

```ffmpeg -i input.mp4 rainbowunicorn.gif```

## view rtsp stream full screen with ffplay

```ffplay -rtsp_transport tcp -i rtsp://user:password@192.168.88.248:554/ipcam_mjpeg.sdp -fs```

## dvgrab

extract from old video camcorder over firewire

```
dvgrab -size=0 -rewind -t mpeg2  -showstatus  -timesys -autosplit=10000
```
and to properly convert it to a mp4 use yadif filter  
```
ffmpeg -i dv-grabbed-video.dv  out.mp4
```
