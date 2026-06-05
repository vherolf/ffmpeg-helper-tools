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
from common import is_video, get_logger

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'sliced_videos')

# filename format: "YYYY-MM-DD HH-MM-SS.ext"  e.g. 2022-05-24 15-46-07.mkv
def video_slicer(root, file, destination, crf=28):
    videoin = os.path.join(root, file)

    video_day, video_time = Path(file).stem.split(' ')
    outdir = Path(destination, video_day, video_time)
    outdir.mkdir(parents=True, exist_ok=True)

    videoout1 = outdir / f'{video_day}_{video_time}_scene1.mkv'
    videoout2 = outdir / f'{video_day}_{video_time}_scene2.mkv'
    videoout3 = outdir / f'{video_day}_{video_time}_scene3.mkv'

    logger.info('%s -> %s', videoin, outdir)
    filter_complex = (
        '[0]split=3[a][b][c];'
        '[a]crop=iw/3:ih:0:0[s1];'
        '[b]crop=iw/3:ih:iw/3:0[s2];'
        '[c]crop=iw/3:ih:(iw/3)*2:0[s3]'
    )
    subprocess.call([
        'ffmpeg', '-i', videoin,
        '-filter_complex', filter_complex,
        '-map', '[s1]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout1,
        '-map', '[s2]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout2,
        '-map', '[s3]', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout3,
        '-y'
    ])

def main(source=video_input_directory, destination=video_output_directory, crf=28):
    Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(source):
        for file in files:
            if is_video(Path(root, file)):
                video_slicer(root, file, destination, crf)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('-c', '--crf', type=int, default=28)
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, crf=args.crf)
