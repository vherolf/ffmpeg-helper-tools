# ffmpeg-helper-tools

Python scripts for batch video processing with ffmpeg. Each script walks a directory recursively, detects video files using ffprobe, and writes output to `~/Desktop/<output_folder>` while mirroring the original directory structure.

## Install

```bash
curl -sSL https://raw.githubusercontent.com/vherolf/ffmpeg-helper-tools/main/install.sh | bash
```

Run the same command again at any time to update.

The script checks for system dependencies (`python3`, `pip3`, `ffmpeg`, `ffprobe`, `git`), clones or pulls the repo to `~/.local/share/ffmpeg-helper-tools`, creates a venv, and installs all packages.

### Manual install

```bash
git clone https://github.com/vherolf/ffmpeg-helper-tools.git
cd ffmpeg-helper-tools
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### System dependencies

| Dependency | Ubuntu/Debian | macOS |
|---|---|---|
| Python 3 | `sudo apt install python3 python3-pip` | `brew install python3` |
| ffmpeg + ffprobe | `sudo apt install ffmpeg` | `brew install ffmpeg` |
| git | `sudo apt install git` | `brew install git` |

## Scripts

### analyzer.py

Prints the path, resolution, codec, and duration for every video found.

```bash
python analyzer.py
python analyzer.py -d /path/to/videos
```

---

### compressor.py

Re-encodes videos to H.265 (libx265) at CRF 28.

```bash
python compressor.py
python compressor.py -s /path/to/videos -d /path/to/output
python compressor.py -c 23               # lower CRF = higher quality (range 0–51)
python compressor.py -n                  # dry run — print actions without encoding
```

Defaults: source = current directory, destination = `~/Desktop/compressed_videos`, CRF = 28.

---

### resizer.py

Resizes videos to 720p height while preserving aspect ratio.

```bash
python resizer.py
python resizer.py -s /path/to/videos -d /path/to/output
python resizer.py -r 1080                # resize to 1080p instead
python resizer.py -n                     # dry run — print actions without resizing
```

Defaults: source = current directory, destination = `~/Desktop/resized_videos`, resolution = 720.

---

### renamer.py

Copies videos with spaces in filenames replaced by underscores.

```bash
python renamer.py
python renamer.py -s /path/to/videos -d /path/to/output
python renamer.py -n                      # dry run — print actions without copying
```

Defaults: source = current directory, destination = `~/Desktop/renamed_videos`.

---

### mosaic.py

Merges pairs of videos found in the same folder side-by-side (default) or stacked vertically. Output goes to `~/Desktop/merged_videos`.

```bash
python mosaic.py                  # horizontal (side-by-side)
python mosaic.py -v               # vertical (stacked)
python mosaic.py -d /path/to/videos
```

Each subfolder must contain exactly 2 video files.

---

### mosaic-left-right.py

Like `mosaic.py` but uses `_left` / `_right` in filenames to determine order. The output filename is derived by stripping the `_left` / `_right` suffix.

```bash
python mosaic-left-right.py
python mosaic-left-right.py -d /path/to/videos
```

---

### videoslicer-horizontal.py

Splits a wide video into 3 equal horizontal scenes using ffmpeg's crop filter.
A video at 5760x1080 produces three 1920x1080 clips.

```bash
python videoslicer-horizontal.py
python videoslicer-horizontal.py -s /path/to/videos -d /path/to/output
```

Filenames must follow the format `YYYY-MM-DD HH-MM-SS.ext` (e.g. `2022-05-24 15-46-07.mkv`).
Output is written to `<destination>/<date>/<time>/`. Defaults: source = current directory, destination = `~/Desktop/sliced_videos`.

---

### videoslicer-vertical.py

Splits a video into 2 equal vertical scenes using ffmpeg's crop filter.
A video at 1920x1080 produces two 960x540 clips.

```bash
python videoslicer-vertical.py
```

Same filename format requirement as `videoslicer-horizontal.py`.

---

### generate-test-media.py

Generates numbered test images (using Pillow) and converts them to videos — useful for testing the other scripts.

```bash
python generate-test-media.py            # generate images + videos
python generate-test-media.py -l         # list available fonts
```

Output is written to `videos/`, `images/`, and `videos_merge/` in the current directory.

---

## common.py

Shared helper used by all scripts. `is_video(filename)` runs ffprobe on the file and returns `True` if it contains a video stream — format-agnostic, works on any container.

---

# FFMPEG Cheatsheet

## convert videos
```ffmpeg -i input.MTS output.mp4```  

## compress videos
crf is 0-52 (23-28 is a good choice)  
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

```ffmpeg -i input.pm4 rainbowunicorn.gif```

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
