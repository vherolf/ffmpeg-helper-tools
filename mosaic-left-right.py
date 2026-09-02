#!/usr/bin/env python
# uses ffmpeg with hstack or vstack complex_filter
# side-by-side merge 2 videos vertical or horizontal
#
# e.g. a video with 2x 1920x1080 scenes will result in a video with 3840x1080
# _____________________
# |         |         |
# | scene 1 | scene 2 |
# |         |         |
# |_________|_________|

import os
from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = os.path.join(home,'Desktop', 'merged_videos')

def build_video_dict(videos, root, file):
    if root in videos:
        videos[root].append(file)
    else:
        videos[root] = [file]

def video_merger(videos, vertical=False, crf=28, dry_run=False):

    for root,files in videos.items():
        if len(files) != 2:
            logger.warning('%s has %d video(s), expected exactly 2 — skipping', root, len(files))
            continue

        try:
            relative_dir = root.removeprefix( str(video_input_directory) )

            videooutdir = Path(video_output_directory, relative_dir.lstrip('/'))

            left = next((f for f in files if Path(f).stem.endswith('_left')), None)
            right = next((f for f in files if Path(f).stem.endswith('_right')), None)
            if left is None or right is None:
                logger.warning("%s: filenames must end with '_left'/'_right' — skipping (%s)", root, files)
                continue

            videoleft = Path(root, left)
            videoright = Path(root, right)
            base_name = Path(left).stem[:-len('_left')]
            videooutfile = Path(videooutdir, base_name + '.mp4')

            logger.info('merging %s + %s -> %s', videoleft.name, videoright.name, videooutfile)
            if dry_run:
                continue

            videooutdir.mkdir(parents=True, exist_ok=True)
            stack = 'vstack' if vertical else 'hstack'
            returncode = subprocess.call(['ffmpeg', '-i', videoleft, '-i', videoright, '-filter_complex', f'{stack}=inputs=2', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), videooutfile, '-y'])
            if returncode == 0:
                logger.info('done %s', videooutfile)
            else:
                logger.error('ffmpeg failed (exit %d) on %s', returncode, root)
        except Exception as e:
            logger.error('failed to merge %s: %s', root, e)

def main(vertical=False, directory=video_input_directory, crf=28, dry_run=False):
    if not dry_run:
        Path(video_output_directory).mkdir(parents=True, exist_ok=True)

    videos = {}
    for root, file in iter_videos(directory):
        build_video_dict(videos, root, file)

    video_merger(videos, vertical=vertical, crf=crf, dry_run=dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vertical", default=False, action="store_true")
    parser.add_argument("-d", "--directory")
    parser.add_argument("-c", "--crf", type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <output>/mosaic-left-right.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(video_output_directory, 'mosaic-left-right.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(vertical=args.vertical, directory=args.directory or video_input_directory, crf=args.crf, dry_run=args.dry_run)
