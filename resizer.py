#!/usr/bin/env python
# recursive batch resizer with ffmpeg

import os
from pathlib import Path
import subprocess
from common import is_video

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'resized_videos')


def video_resize(root, file, source, destination, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/').replace(' ', '_'))
    videoout = Path(videooutdir, videoin.stem.replace(' ', '_') + '.mp4')
    print('resize', videoin, 'to', videoout)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    ## resize to half size and compress
    #subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=iw/2:ih/2', '-crf', '23', '-c:a', 'copy', videoout, '-y'])
    ## resize to half size only
    #subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=iw/2:ih/2', '-c:a', 'copy', videoout, '-y'])
    ## resize to 720p, keep aspect ratio
    subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=-1:720', '-c:a', 'copy', videoout, '-y'])

def main(source=video_input_directory, destination=video_output_directory, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(source):
        for file in files:
            if is_video(file):
                video_resize(root, file, source, destination, dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, dry_run=args.dry_run)
