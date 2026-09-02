from pathlib import Path
import ffmpeg
from common import get_logger, add_file_handler, iter_videos

logger = get_logger(__name__)

video_input_directory = Path.cwd()

def main(directory = video_input_directory):
    for root, file in iter_videos(directory):
        video = Path(root, file)
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
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: ./analyzer.log)')
    args = parser.parse_args()

    if args.log_file:
        log_path = Path('analyzer.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)

    main(directory = args.directory or video_input_directory)