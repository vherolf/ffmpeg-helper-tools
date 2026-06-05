#!/usr/bin/env python
# recursive batch compressor with ffmpeg

import os
from pathlib import Path
import subprocess
from common import is_video

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'compressed_videos')


def video_compressor(root, file, source, destination, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/'))
    videoout = Path(videooutdir, videoin.stem + '.mp4')
    print('compressing', videoin, 'to', videoout)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    ## compress the videos with ffmpeg to h.265 (better)
    #subprocess.call(['ffmpeg', '-i', videoin, '-vcodec', 'libx265','-crf', '28', '-c:a', 'copy', videoout, '-y' ])
    ## compress the videos with ffmpeg to h.264 (for legacy systems)
    subprocess.call(['ffmpeg', '-i', videoin, '-crf', '28', '-c:a', 'copy', videoout, '-y'])

def main(source=video_input_directory, destination=video_output_directory, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(Path(source)):
        for file in files:
            if is_video(file):
                video_compressor(root, file, source, destination, dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, dry_run=args.dry_run)
