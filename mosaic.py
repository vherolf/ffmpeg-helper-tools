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
import queue

q = queue.Queue()

# define users home directory
home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = os.path.join(home,'Desktop', 'merged_videos')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

# video container that script searches for
mimetype = '.mp4'
#mimetype = '.MTS'

videos = {}

def build_video_dict(root, file):
    # build video dictionary list 
    if root in  videos.keys():
        videos[root].append(file)
    else:
        videos[root] = [file]

def video_merger(videos, vertical=False):

    for root,files in videos.items():
        #check if only 2 videos in folder
        print(root, files)

        #videooutdir =  Path(video_output_directory, relative_dir.lstrip('/') )
        #videooutdir.mkdir(parents=True, exist_ok=True)
        #videoout = Path(videooutdir , videoin.stem +'.mp4')

        relative_dir = root.removeprefix( str(video_input_directory) )
        videotop = Path(root, files[0])
        videobottom = Path(root, files[1])
        
        videooutdir = Path(video_output_directory, relative_dir.lstrip('/'))
        videooutdir.mkdir(parents=True, exist_ok=True)
        videooutfile = Path(videooutdir, 'out.mp4' )

        print( videooutfile, videobottom, videotop)

        if vertical == False:
            # side-by-side merge the videos horizontal with ffmpeg hstack
            subprocess.call(['ffmpeg', '-i', videotop ,'-i', videobottom ,'-filter_complex','hstack=inputs=2', videooutfile, '-y'])
        elif vertical == True:
            # side-by-side merge the videos vertical with ffmpeg vstack
            subprocess.call(['ffmpeg', '-i', videotop ,'-i', videobottom ,'-filter_complex','vstack=inputs=2', videooutfile, '-y'])

def main(vertical=False):
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                build_video_dict(root, file)

    video_merger(videos, vertical=vertical)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vertical",default=False, action="store_true")
    args = parser.parse_args()

    if args.vertical:
        main(vertical=True)
    else:
        main(vertical=False)
