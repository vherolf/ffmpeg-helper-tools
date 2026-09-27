#!/usr/bin/env python
# uses ffmpeg crop filter
# slices a video in 2 eqal vertical scenes
# a video with 1920x1080 will be cut into a top and a bottom half
# two videos with 1920x540
#  _________
# |         |
# | scene 1 |
# |_________|
# |         |
# | scene 2 |
# |_________|

import os
from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos

# define users home directory
logger = get_logger(__name__)

home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output = os.path.join(home,'Desktop', 'sliced_videos')

# nameing of the file should be "date" + space + "time"
# eg:   2022-05-24 15-46-07.mkv
def video_slicer(root, file, destination, crf=28, dry_run=False):
    videoin = os.path.join(root, file)

    video_day, video_time = Path(file).stem.split(' ')
    outdir = Path(destination, video_day, video_time)

    videoout1 = outdir / f'{video_day}_{video_time}_scene1.mkv'
    videoout2 = outdir / f'{video_day}_{video_time}_scene2.mkv'

    logger.info('%s -> %s', videoin, outdir)
    if dry_run:
        return
    outdir.mkdir(parents=True, exist_ok=True)
    rc1 = subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw:ih/2:0:0',    '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout1, '-y'])
    rc2 = subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw:ih/2:0:ih/2', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout2, '-y'])
    if rc1 == 0 and rc2 == 0:
        logger.info('done %s', outdir)
    else:
        logger.error('ffmpeg failed (exit %d/%d) on %s', rc1, rc2, videoin)

def main(source=video_input_directory, destination=video_output, crf=28, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, file in iter_videos(source):
        try:
            video_slicer(root, file, destination, crf, dry_run)
        except ValueError:
            logger.error("%s doesn't match the expected 'YYYY-MM-DD HH-MM-SS.ext' filename format — skipping", Path(root, file))
        except Exception as e:
            logger.error('failed on %s: %s', Path(root, file), e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output)
    parser.add_argument('-c', '--crf', type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/videoslicer-vertical.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'videoslicer-vertical.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, crf=args.crf, dry_run=args.dry_run)
