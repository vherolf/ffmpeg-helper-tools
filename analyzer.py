from pathlib import Path
import ffmpeg
import os
from common import is_video, get_logger

logger = get_logger(__name__)

video_input_directory = Path.cwd()

def main(directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            if is_video(file):
                video = Path(root, file)
                v = ffmpeg.probe(video)["streams"][0]
                logger.info('%s  %sx%s  %s  %ss', video, v['width'], v['height'], v['codec_name'], v['duration'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        main(directory = args.directory)
    else:
        main(directory = video_input_directory)