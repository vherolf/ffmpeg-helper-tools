# ffmpeg-helper-tools

Python scripts for batch video processing with ffmpeg. Each script walks a directory recursively, detects video files using ffprobe.

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/vherolf/ffmpeg-helper-tools/main/install.sh | bash
```

Run the same command again at any time to update.

The script checks for system dependencies (`python3`, `pip3`, `ffmpeg`, `ffprobe`, `git`, and — non-blocking — `libmagic` and the FreeMono font), clones or pulls the repo into `./ffmpeg-helper-tools` (relative to where you run the command), creates a venv, and installs all packages.

### System dependencies

**Ubuntu / Debian:** `sudo apt install -y git python3 python3-pip python3-venv ffmpeg`

**macOS:** `brew install git python3 ffmpeg`

`archiver.py` additionally needs `libmagic1` (Ubuntu/Debian) / `libmagic` (macOS) — the installer checks for it and warns if missing, but won't block the rest of the install.

`generate-test-media.py` additionally needs the FreeMono font: `sudo apt install fonts-freefont-ttf` (Ubuntu/Debian) / `brew install --cask font-freefont` (macOS). It also needs an ffmpeg built with `libfreetype` (text drawing) and `libsvtav1` (AV1) — the standard Ubuntu/Debian and Homebrew packages include both. Check with `ffmpeg -filters | grep drawtext` and `ffmpeg -encoders | grep svtav1`.

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

Generates solid color test videos with a running seconds counter in the middle and the frame number at the bottom — useful for testing the other scripts. It also writes still test images (a digit 0–6 on each color, `images/<color><digit>-<height>p.png`, e.g. `blue3-720p.png`) for testing ffmpeg with pictures.

Videos are named `<color>-<duration>-<height>p.mp4` (e.g. `blue-60-720p.mp4`) for the colors blue, green, white, red, pink and darkgrey and the durations 30 and 60 seconds (720p by default, 25 fps, a quiet looping C major tune as AAC audio, CPU encoding).

`--resolution` takes heights in pixels; the width follows at 16:9 (480 → 854x480, 720 → 1280x720, 1080 → 1920x1080, 2160 → 3840x2160). Text sizes scale with the height, so every resolution looks the same, just sharper.

```bash
python generate-test-media.py                                  # x264 and av1, all colors and durations
python generate-test-media.py --codec av1                      # only av1
python generate-test-media.py --color blue red --duration 30   # a subset
python generate-test-media.py --duration 720                   # 720 second videos instead of 30 and 60
python generate-test-media.py --duration 10 120                # several lengths at once, one set per length
python generate-test-media.py --resolution 1080                # 1080p instead of 720p
python generate-test-media.py --resolution 720 1080 2160       # several resolutions at once
python generate-test-media.py -c 30                            # same crf for every codec
python generate-test-media.py --images-only                    # only the png test images
python generate-test-media.py -l                               # list available fonts
```

Output is written to subfolders of `videos/` in the current directory. Both codecs play in Chrome, Firefox, Edge and Safari 17+:

| Folder | Codec | Default CRF |
|---|---|---|
| `videos/x264/` | H.264 (libx264) | 23 |
| `videos/av1/` | AV1 (libsvtav1) | 35 |

**Test input for the other scripts** (10 seconds each, per codec and resolution, generated in the same run):

| Folder | For | Content |
|---|---|---|
| `mosaic/<left>-<right>-<height>p/` | `mosaic.py`, `mosaic-left-right.py` | exactly 2 counter videos, `<pair>_left.mp4` and `<pair>_right.mp4` — pairs blue/green, red/white, pink/darkgrey |
| `videoslicer-horizontal/<height>p/` | `videoslicer-horizontal.py` | `2000-01-01 00-00-10.mp4`, 3 scenes side by side (3840x720 at 720p) |
| `videoslicer-vertical/<height>p/` | `videoslicer-vertical.py` | `2000-01-01 00-00-10.mp4`, 2 scenes stacked (1280x720 at 720p) |

Every scene has its own color, a `scene N` label, the counter and the frame number, so after slicing or merging you can see right away that each piece is the right one and still in sync.

```bash
python mosaic.py -s videos/x264/mosaic -d /tmp/merged
python mosaic-left-right.py -d videos/x264/mosaic
python videoslicer-horizontal.py -s videos/x264/videoslicer-horizontal -d /tmp/sliced
python videoslicer-vertical.py -s videos/x264/videoslicer-vertical -d /tmp/sliced
```

**Sound:** a quiet music-box style tune that loops every 4 seconds — C E G C G E C, then a half second rest. Each note is a short pluck that fades out, and a note starts on every full second when the counter changes, so you can hear if audio and video drift apart after a cut or merge. No audio files are involved: ffmpeg's `aevalsrc` computes the sound from a formula built by `melody_expression()`. To change it, edit in `generate-test-media.py`:

- `MELODY = [0, 4, 7, 12, 7, 4, 0, None]` — semitones above middle C, one per half second, `None` is a rest
- `volume=0.06` in `generate_counter_video()` — louder or quieter (peaks around -24 dB now)
- `basefrequency=261.63` in `melody_expression()` — moves the whole tune higher or lower

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
