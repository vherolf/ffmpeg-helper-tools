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

# define users home directory
home = str(Path.home())

# video input files (current directory)
video_input_directory = Path.cwd()

print(video_input_directory)
# video output directory
video_output = os.path.join(home,'Desktop', 'sliced_videos')
Path(video_output).mkdir(parents=True, exist_ok=True)

# video container that script searches for
mimetype = '.mkv'

# nameing of the file should be "date" + space + "time"
# eg:   2022-05-24 15-46-07.mkv  
def video_slicer(root, file):
    videoin =  os.path.join(root, file)
    
    # create folders depending on date and time in filename
    video_day, video_time = Path(file).stem.split(' ')
    print(video_day, video_time)
    Path(video_output, video_day, video_time).mkdir(parents=True, exist_ok=True)
    
    videoout1 =  os.path.join(video_output, video_day, video_time, video_day+'_'+video_time+'_scene1'+'.mkv')
    videoout2 =  os.path.join(video_output, video_day, video_time, video_day+'_'+video_time+'_scene2'+'.mkv')

    # slice the videos with ffmpeg
    subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw/2:ih/2:0:0',    '-c:a', 'copy', videoout1, '-y' ])
    subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw/2:ih/2:0:ih/2', '-c:a', 'copy', videoout2, '-y'])

def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                print(file)
                video_slicer(root,file)
    
if __name__ == '__main__':
    main()
