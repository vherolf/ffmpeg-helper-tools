#!/usr/bin/env python
# uses ffmpeg crop filter
# slices a video in 2 eqal vertical scenes
# a video with 1920x1080 will be cuted vertical
# in two videos with 960x540 
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
from common import is_video, get_logger

# define users home directory
logger = get_logger(__name__)

home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output = os.path.join(home,'Desktop', 'sliced_videos')
Path(video_output).mkdir(parents=True, exist_ok=True)

# nameing of the file should be "date" + space + "time"
# eg:   2022-05-24 15-46-07.mkv  
def video_slicer(root, file, destination, crf=28):
    videoin = os.path.join(root, file)

    video_day, video_time = Path(file).stem.split(' ')
    outdir = Path(destination, video_day, video_time)
    outdir.mkdir(parents=True, exist_ok=True)

    videoout1 = outdir / f'{video_day}_{video_time}_scene1.mkv'
    videoout2 = outdir / f'{video_day}_{video_time}_scene2.mkv'

    logger.info('%s -> %s', videoin, outdir)
    subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw:ih/2:0:0',    '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout1, '-y'])
    subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw:ih/2:0:ih/2', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), '-c:a', 'copy', videoout2, '-y'])

def main(source=video_input_directory, destination=video_output, crf=28):
    Path(destination).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(source):
        for file in files:
            if is_video(Path(root, file)):
                video_slicer(root, file, destination, crf)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output)
    parser.add_argument('-c', '--crf', type=int, default=28)
    args = parser.parse_args()
    main(source=args.source, destination=args.destination, crf=args.crf)
