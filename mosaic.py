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

from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

# video input files (current directory)
video_input_directory = Path.cwd()

def build_video_dict(videos, root, file):
    if root in videos:
        videos[root].append(file)
    else:
        videos[root] = [file]

def video_merger(videos, source, destination, vertical=False, crf=28, dry_run=False):

    for root,files in videos.items():
        if len(files) != 2:
            logger.warning('%s has %d video(s), expected exactly 2 — skipping', root, len(files))
            continue

        try:
            relative_dir = root.removeprefix(str(source))
            videotop = Path(root, files[0])
            videobottom = Path(root, files[1])

            videooutdir = Path(destination, relative_dir.lstrip('/'))
            videooutfile = Path(videooutdir, 'out.mp4')

            logger.info('merging %s + %s -> %s', videotop.name, videobottom.name, videooutfile)
            if dry_run:
                continue

            videooutdir.mkdir(parents=True, exist_ok=True)
            stack = 'vstack' if vertical else 'hstack'
            returncode = subprocess.call(['ffmpeg', '-i', videotop, '-i', videobottom, '-filter_complex', f'{stack}=inputs=2', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), videooutfile, '-y'])
            if returncode == 0:
                logger.info('done %s', videooutfile)
            else:
                logger.error('ffmpeg failed (exit %d) on %s', returncode, root)
        except Exception as e:
            logger.error('failed to merge %s: %s', root, e)

def main(source=video_input_directory, destination=video_input_directory, vertical=False, crf=28, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)

    videos = {}
    for root, file in iter_videos(source):
        build_video_dict(videos, root, file)

    video_merger(videos, source=source, destination=destination, vertical=vertical, crf=crf, dry_run=dry_run)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", default=video_input_directory)
    parser.add_argument("-d", "--destination", default=video_input_directory)
    parser.add_argument("-v", "--vertical", default=False, action="store_true")
    parser.add_argument("-c", "--crf", type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/mosaic.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'mosaic.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, vertical=args.vertical, crf=args.crf, dry_run=args.dry_run)
