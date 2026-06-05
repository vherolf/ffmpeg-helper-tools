#!/usr/bin/env python
# recursive batch compressor with ffmpeg

import os
from pathlib import Path
import subprocess
from common import is_video, get_logger

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'compressed_videos')


def video_compressor(root, file, source, destination, crf=28, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/'))
    videoout = Path(videooutdir, videoin.stem + '.mp4')
    logger.info('compressing %s -> %s (h.265 crf=%d)', videoin, videoout, crf)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    subprocess.call(['ffmpeg', '-i', videoin, '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout, '-y'])

def main(source=video_input_directory, destination=video_output_directory, crf=28, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(Path(source)):
        for file in files:
            if is_video(file):
                video_compressor(root, file, source, destination, crf, dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-c', '--crf', type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, crf=args.crf, dry_run=args.dry_run)
