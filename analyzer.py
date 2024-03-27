from pathlib import Path
import ffmpeg
import sys, os

# video input files (current directory)
video_input_directory = Path.cwd()

mimetype = 'mp4'

def main():
    for root, dirs, files in os.walk( video_input_directory ):
        for file in files:
            if file.endswith( mimetype ):
                video = Path(root, file)
                v = ffmpeg.probe(video)["streams"][0]
                print(video, v['width'], v['height'], v['codec_name'], v['duration'])
    
if __name__ == '__main__':
    main()