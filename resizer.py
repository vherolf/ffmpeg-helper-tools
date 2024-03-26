# recursive batch resizer with ffmpeg

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
#mimetype = '.mkv'
mimetype = '.MTS'
#mimetype = '.MP4'
#mimetype = '.mp4'

def video_resize(root, file):
    # make relative directory structure in output location
    relative_dir = root.removeprefix( str(video_input_directory) )

    videoin =  Path(root, file)
      
    videooutdir =  Path(video_output_directory, relative_dir.lstrip('/') )
    videooutdir.mkdir(parents=True, exist_ok=True)
    videoout = Path(videooutdir , videoin.stem +'.mp4')
    
    print('compressing', videoin, 'to', videoout)
    # search ffmpeg resize 
    #subprocess.call(['ffmpeg', '-i', videoin, '-crf', '28', '-c:a', 'copy', videoout, '-y' ])
    
def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                video_resize(root, file)
    
if __name__ == '__main__':
    main()
