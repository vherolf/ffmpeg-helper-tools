#!/usr/bin/env python
# uses ffmpeg crop filter
# slices a video in 3 eqal vertical scenes
# e.g. a video with 5780x1080 will make 3x 1920x1080 scenes
# _______________________________
# |         |         |         |
# | scene 1 | scene 2 | scene 3 |
# |         |         |         |
# |_________|_________|_________|

import os
from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'sliced_videos')

# filename format: "YYYY-MM-DD HH-MM-SS.ext"  e.g. 2022-05-24 15-46-07.mkv
def video_slicer(root, file, destination, crf=28, dry_run=False):
    videoin = os.path.join(root, file)

    video_day, video_time = Path(file).stem.split(' ')
    outdir = Path(destination, video_day, video_time)

    videoout1 = outdir / f'{video_day}_{video_time}_scene1.mkv'
    videoout2 = outdir / f'{video_day}_{video_time}_scene2.mkv'
    videoout3 = outdir / f'{video_day}_{video_time}_scene3.mkv'

    logger.info('%s -> %s', videoin, outdir)
    if dry_run:
        return
    outdir.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        '[0]split=3[a][b][c];'
        '[a]crop=iw/3:ih:0:0[s1];'
        '[b]crop=iw/3:ih:iw/3:0[s2];'
        '[c]crop=iw/3:ih:(iw/3)*2:0[s3]'
    )
    returncode = subprocess.call([
        'ffmpeg', '-i', videoin,
        '-filter_complex', filter_complex,
        '-map', '[s1]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout1,
        '-map', '[s2]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout2,
        '-map', '[s3]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout3,
        '-y'
    ])
    if returncode == 0:
        logger.info('done %s', outdir)
    else:
        logger.error('ffmpeg failed (exit %d) on %s', returncode, videoin)

def main(source=video_input_directory, destination=video_output_directory, crf=28, dry_run=False):
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
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-c', '--crf', type=int, default=28)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/videoslicer-horizontal.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'videoslicer-horizontal.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, crf=args.crf, dry_run=args.dry_run)
