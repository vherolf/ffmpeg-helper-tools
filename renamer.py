#!/usr/bin/env python
# recursive batch resname with ffmpeg

import os
from pathlib import Path
import shutil
from common import is_video

# define users home directory
home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = Path(home,'Desktop', 'renamed_videos')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

def video_rename(root, file):
    # make relative directory structure in output location
    relative_dir = root.removeprefix( str(video_input_directory) )

    videoin =  Path(root, file)
      
    videooutdir =  Path(video_output_directory, relative_dir.lstrip('/') )
    videooutdir.mkdir(parents=True, exist_ok=True)
    videoout = Path(videooutdir , videoin.stem.replace(" ", "_") +'.mp4')
    
    print('rename', videoin, 'to', videoout)
    #shutil.move(videoin, videoout)

def main(directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            if is_video(file):
                video_rename(root, file)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        main(directory = args.directory)
    else:
        main(directory = video_input_directory)
