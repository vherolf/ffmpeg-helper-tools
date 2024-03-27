#!/usr/bin/env python
# recursive batch compressor with ffmpeg

import os
from pathlib import Path
import subprocess

# define users home directory
home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

# video output directory
video_output_directory = Path(home,'Desktop', 'compressed_videos')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

# video container that script searches for
mimetype = ['.mp4','.MP4','.MTS','mkv']

def video_compressor(root, file):
    # make relative directory structure in output location
    relative_dir = root.removeprefix( str(video_input_directory) )

    videoin =  Path(root, file)
      
    videooutdir =  Path(video_output_directory, relative_dir.lstrip('/') )
    videooutdir.mkdir(parents=True, exist_ok=True)
    videoout = Path(videooutdir , videoin.stem +'.mp4')
    
    print('compressing', videoin, 'to', videoout)
    ## compress the videos with ffmpeg to h.265 (better)
    #subprocess.call(['ffmpeg', '-i', videoin, '-vcodec', 'libx265','-crf', '28', '-c:a', 'copy', videoout, '-y' ])
    ## compress the videos with ffmpeg to h.264 (for legacy systems)
    subprocess.call(['ffmpeg', '-i', videoin, '-crf', '28', '-c:a', 'copy', videoout, '-y' ])
    
def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension in mimetype:
                video_compressor(root, file)

if __name__ == '__main__':
    main()
