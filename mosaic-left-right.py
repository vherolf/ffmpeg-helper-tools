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
#mimetype = '.mp4'
#mimetype = '.MTS'
mimetype = ['.mp4', '.MP4', '.MTS','mkv']

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
        #print(root, files)

        relative_dir = root.removeprefix( str(video_input_directory) )
        
        #videoright = Path(root, files[0])
        #videoleft = Path(root, files[1])
        
        videooutdir = Path(video_output_directory, relative_dir.lstrip('/'))
        videooutdir.mkdir(parents=True, exist_ok=True)
        #videooutfile = Path(videooutdir, 'out.mp4' )

        if files[0].find('right') != -1:
            video = files[0].split('right')
            #print("right", files[0], videoright)
            videooutfile = Path(videooutdir, video[0].rstrip('_') +'.mp4')
            videoleft = Path(root, files[1])
            videoright = Path(root, files[0])
            print(videoright)
            print()
        else:
            video = files[0].split('left')
            #print("left", files[0], videoleft)
            videooutfile = Path(videooutdir, video[0].rstrip('_') + '.mp4')
            videoleft = Path(root, files[0])
            videoright = Path(root, files[1])
            print(videoright)
            print()

        if vertical == False:
            # side-by-side merge the videos horizontal with ffmpeg hstack
            subprocess.call(['ffmpeg', '-i', videoleft ,'-i', videoright ,'-filter_complex','hstack=inputs=2', '-crf', '25', videooutfile, '-y'])
            #pass

        elif vertical == True:
            # side-by-side merge the videos vertical with ffmpeg vstack
            #subprocess.call(['ffmpeg', '-i', videotop ,'-i', videobottom ,'-filter_complex','vstack=inputs=2', videooutfile, '-y'])
            pass

#def main(vertical=False):
#    for root, dirs, files in os.walk( video_input_directory ):
#        for file in files:
#            if file.endswith( mimetype ):
#                build_video_dict(root, file)

def main(vertical=False, directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension in mimetype:
                build_video_dict(root, file)

    video_merger(videos, vertical=vertical)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vertical",default=False, action="store_true")
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        directory = args.directory
    else:
        directory = video_input_directory

    if args.vertical:
        main(vertical=True, directory = directory)
    else:
        main(vertical=False, directory = directory)
