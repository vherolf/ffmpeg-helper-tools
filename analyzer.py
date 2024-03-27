from pathlib import Path
import ffmpeg
import sys, os

# video input files (current directory)
video_input_directory = Path.cwd()

mimetype = ['.mp4','.MP4','.MTS','mkv']

def main(directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension in mimetype:
                video = Path(root, file)
                v = ffmpeg.probe(video)["streams"][0]
                print(video, v['width'], v['height'], v['codec_name'], v['duration'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        main(directory = args.directory)
    else:
        main(directory = video_input_directory)