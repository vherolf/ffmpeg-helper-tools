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

def video_merger(videos):

    for root,files in videos.items():
        #check if only 2 videos in folder
        print(root, files)

        #videooutdir =  Path(video_output_directory, relative_dir.lstrip('/') )
        #videooutdir.mkdir(parents=True, exist_ok=True)
        #videoout = Path(videooutdir , videoin.stem +'.mp4')

        relative_dir = root.removeprefix( str(video_input_directory) )
        videotop = Path(root, files[0])
        videobottom = Path(root, files[1])
        
        videoout = Path(video_output_directory)

        print(relative_dir, videoout, videobottom, videotop)

    # side-by-side merge the videos with ffmpeg
    #subprocess.call(['ffmpeg', '-i', videotop ,'-i', videobottom ,'-filter_complex','[0:v][1:v]hstack,format=yuv420p[v];[0:a][1:a]amerge[a]','-map','[v]','-map','[a]','-c:v','libx264','-crf 23','-ac','2', videoout])

def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                build_video_dict(root, file)

    video_merger(videos)
    #print(videos)

if __name__ == '__main__':
    main()
