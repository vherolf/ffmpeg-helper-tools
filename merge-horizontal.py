# uses ffmpeg
# side-by-side merge 2 videos
# a video with 2x 1920x1080 scenes will result in a video with 3840x1080
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
video_output = os.path.join(home,'Desktop', 'merged_videos')
Path(video_output).mkdir(parents=True, exist_ok=True)

# video container that script searches for
mimetype = '.mp4'
#mimetype = '.MTS'

videos = {}
 
def video_merger(root, file):
    #videoin =  os.path.join(root, file)
    print(root, file)
    
    # create folders depending on date and time in filename
    # build dict list
    if root in  videos.keys():
        videos[root].append(file)
    else:
        videos[root] = [file]

    #ffmpeg -i left.avi -i right.avi -filter_complex "[0:v][1:v]hstack,format=yuv420p[v];[0:a][1:a]amerge[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 23 -ac 2 output.mp4
    
    
    #videoin1 =  os.path.join(video_output, video_day, video_time, video_day+'_'+video_time+'_scene1'+'.mkv')
    #videoin2 =  os.path.join(video_output, '_'+video_time+'_scene2'+'.mkv')

    # side-by-side merge the videos with ffmpeg
    #subprocess.call(['ffmpeg', '-i', videoin, '-filter:v', 'crop=iw/3:ih:0:0',    '-c:a', 'copy', videoout1, '-y' ])
    #ffmpeg -i left.avi -i right.avi -filter_complex "[0:v][1:v]hstack,format=yuv420p[v];[0:a][1:a]amerge[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 23 -ac 2 output.mp4
def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                video_merger(root,file)
    print(videos)

if __name__ == '__main__':
    main()
