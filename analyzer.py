from pathlib import Path
import ffmpeg
import os
from common import is_video, get_logger

logger = get_logger(__name__)

video_input_directory = Path.cwd()

def main(directory = video_input_directory):
    for root, dirs, files in os.walk( directory ):
        for file in files:
            video = Path(root, file)
            if is_video(video):
                try:
                    probe = ffmpeg.probe(video)
                    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                    duration = v.get('duration') or probe['format'].get('duration', 'unknown')
                    logger.info('%s  %sx%s  %s  %ss', video, v['width'], v['height'], v['codec_name'], duration)
                except (StopIteration, KeyError, ffmpeg.Error) as e:
                    logger.warning('could not read metadata for %s: %s', video, e)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()

    if args.directory:
        main(directory = args.directory)
    else:
        main(directory = video_input_directory)