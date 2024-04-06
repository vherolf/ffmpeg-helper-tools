#!/usr/bin/env python
# recursive batch trim videos with ffmpeg 

import os
from pathlib import Path
import subprocess

# define users home directory
home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = Path(home,'Desktop', 'resized_videos')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

# video container that script searches for
mimetype = ['.mp4','.MP4','.MTS','mkv']

def video_resize(root, file):
    # make relative directory structure in output location
    relative_dir = root.removeprefix( str(video_input_directory) )

    videoin =  Path(root, file)
      
    videooutdir =  Path(video_output_directory, relative_dir.lstrip('/').replace(' ','_') )
    videooutdir.mkdir(parents=True, exist_ok=True)
    # also fix filename
    videoout = Path(videooutdir , videoin.stem.replace(' ','_') +'.mp4')
    
    print('resize', videoin, 'to', videoout)
    ## ffmpeg resize to half size and compress  
    #subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=iw/2:ih/2', '-crf', '23', '-c:a', 'copy', videoout, '-y' ])
    ## resize only to half size
    #subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=iw/2:ih/2', '-c:a', 'copy', videoout, '-y' ])
    ## resize, but keep ratio
    subprocess.call(['ffmpeg', '-i', videoin, '-vf', 'scale=-1:720', '-c:a', 'copy', videoout, '-y' ])

def main(directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension in mimetype:
                video_resize(root, file)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        main(directory = args.directory)
    else:
        main(directory = video_input_directory)
