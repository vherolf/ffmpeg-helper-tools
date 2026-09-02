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
from common import is_video, get_logger

# define users home directory
logger = get_logger(__name__)

home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = os.path.join(home,'Desktop', 'merged_videos')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

videos = {}

def build_video_dict(root, file):
    # build video dictionary list 
    if root in  videos.keys():
        videos[root].append(file)
    else:
        videos[root] = [file]

def video_merger(videos, vertical=False, crf=28):

    for root,files in videos.items():
        if len(files) != 2:
            logger.warning('%s has %d video(s), expected exactly 2 — skipping', root, len(files))
            continue

        try:
            relative_dir = root.removeprefix( str(video_input_directory) )

            videooutdir = Path(video_output_directory, relative_dir.lstrip('/'))
            videooutdir.mkdir(parents=True, exist_ok=True)

            if files[0].find('right') != -1:
                video = files[0].split('right')
                videooutfile = Path(videooutdir, video[0].rstrip('_') +'.mp4')
                videoleft = Path(root, files[1])
                videoright = Path(root, files[0])
            else:
                video = files[0].split('left')
                videooutfile = Path(videooutdir, video[0].rstrip('_') + '.mp4')
                videoleft = Path(root, files[0])
                videoright = Path(root, files[1])

            logger.info('merging %s + %s -> %s', videoleft.name, videoright.name, videooutfile)

            stack = 'vstack' if vertical else 'hstack'
            returncode = subprocess.call(['ffmpeg', '-i', videoleft, '-i', videoright, '-filter_complex', f'{stack}=inputs=2', '-c:v', 'libx265', '-preset', 'slow', '-crf', str(crf), videooutfile, '-y'])
            if returncode == 0:
                logger.info('done %s', videooutfile)
            else:
                logger.error('ffmpeg failed (exit %d) on %s', returncode, root)
        except Exception as e:
            logger.error('failed to merge %s: %s', root, e)

#def main(vertical=False):
#    for root, dirs, files in os.walk( video_input_directory ):
#        for file in files:
#            if file.endswith( mimetype ):
#                build_video_dict(root, file)

def main(vertical=False, directory=video_input_directory, crf=28):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            if is_video(Path(root, file)):
                build_video_dict(root, file)

    video_merger(videos, vertical=vertical, crf=crf)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vertical", default=False, action="store_true")
    parser.add_argument("-d", "--directory")
    parser.add_argument("-c", "--crf", type=int, default=28)
    args = parser.parse_args()
    main(vertical=args.vertical, directory=args.directory or video_input_directory, crf=args.crf)
