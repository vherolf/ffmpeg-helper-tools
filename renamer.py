#!/usr/bin/env python
# recursive batch rename with ffmpeg

from pathlib import Path
import shutil
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'renamed_videos')


def video_rename(root, file, source, destination, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/'))
    videoout = Path(videooutdir, videoin.stem.replace(' ', '_') + videoin.suffix)
    logger.info('rename %s -> %s', videoin, videoout)
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(videoin, videoout)
    logger.info('done %s', videoout)

def main(source=video_input_directory, destination=video_output_directory, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, file in iter_videos(source):
        try:
            video_rename(root, file, source, destination, dry_run)
        except Exception as e:
            logger.error('failed on %s: %s', Path(root, file), e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/renamer.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'renamer.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, dry_run=args.dry_run)
