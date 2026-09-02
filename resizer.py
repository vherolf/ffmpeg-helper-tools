#!/usr/bin/env python
# recursive batch resizer with ffmpeg

from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'resized_videos')


def video_resize(root, file, source, destination, resolution=720, crf=28, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/').replace(' ', '_'))
    videoout = Path(videooutdir, videoin.stem.replace(' ', '_') + '.mp4')
    logger.info('resize %s -> %s (%dp crf=%d)', videoin, videoout, resolution, crf)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    returncode = subprocess.call(['ffmpeg', '-i', videoin, '-vf', f'scale=-2:{resolution}', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout, '-y'])
    if returncode == 0:
        logger.info('done %s', videoout)
    else:
        logger.error('ffmpeg failed (exit %d) on %s', returncode, videoin)

def main(source=video_input_directory, destination=video_output_directory, resolution=720, crf=28, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, file in iter_videos(source):
        try:
            video_resize(root, file, source, destination, resolution, crf, dry_run)
        except Exception as e:
            logger.error('failed on %s: %s', Path(root, file), e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-r', '--resolution', type=int, default=720)
    parser.add_argument('-c', '--crf', type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/resizer.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'resizer.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, resolution=args.resolution, crf=args.crf, dry_run=args.dry_run)
