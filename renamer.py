#!/usr/bin/env python
# recursive batch rename with ffmpeg

import os
from pathlib import Path
import shutil
from common import is_video, get_logger

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'renamed_videos')


def video_rename(root, file, source, destination, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/'))
    videoout = Path(videooutdir, videoin.stem.replace(' ', '_') + '.mp4')
    logger.info('rename %s -> %s', videoin, videoout)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(videoin, videoout)

def main(source=video_input_directory, destination=video_output_directory, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(source):
        for file in files:
            if is_video(Path(root, file)):
                video_rename(root, file, source, destination, dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, dry_run=args.dry_run)
