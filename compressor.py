#!/usr/bin/env python
# recursive batch compressor with ffmpeg

from pathlib import Path
import subprocess
from common import get_logger, add_file_handler, iter_videos, VIDEO_CODECS, video_encoder_args, audio_encoder_args

logger = get_logger(__name__)

home = str(Path.home())

video_input_directory = Path.cwd()
video_output_directory = Path(home, 'Desktop', 'compressed_videos')


# re-encode to a browser compatible mp4, x264 by default or av1
# aac and mp3 audio is copied, other audio is converted to aac
def video_compressor(root, file, source, destination, codec='x264', crf=None, dry_run=False):
    relative_dir = root.removeprefix(str(source))
    videoin = Path(root, file)
    videooutdir = Path(destination, relative_dir.lstrip('/'))
    videoout = Path(videooutdir, videoin.stem + '.mp4')
    logger.info('compressing %s -> %s (%s crf=%s)', videoin, videoout, codec, crf if crf is not None else VIDEO_CODECS[codec]['crf'])
    if dry_run:
        return
    videooutdir.mkdir(parents=True, exist_ok=True)
    returncode = subprocess.call(['ffmpeg', '-i', videoin, *video_encoder_args(codec, crf), *audio_encoder_args(videoin), videoout, '-y'])
    if returncode == 0:
        logger.info('done %s', videoout)
    else:
        logger.error('ffmpeg failed (exit %d) on %s', returncode, videoin)

def main(source=video_input_directory, destination=video_output_directory, codec='x264', crf=None, dry_run=False):
    if not dry_run:
        Path(destination).mkdir(parents=True, exist_ok=True)
    for root, file in iter_videos(source):
        try:
            video_compressor(root, file, source, destination, codec, crf, dry_run)
        except Exception as e:
            logger.error('failed on %s: %s', Path(root, file), e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default=video_input_directory)
    parser.add_argument('-d', '--destination', default=video_output_directory)
    parser.add_argument('--codec', choices=list(VIDEO_CODECS), default='x264',
                        help='x264 (default) or av1, both play in all browsers')
    parser.add_argument('-c', '--crf', type=int, default=None,
                        help='quality, lower = better (default: x264 23, av1 35)')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-l', '--log-file', nargs='?', const=True,
                         help='also write log output to a file (default: <destination>/compressor.log)')
    args = parser.parse_args()
    if args.log_file:
        log_path = Path(args.destination, 'compressor.log') if args.log_file is True else Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)
    main(source=args.source, destination=args.destination, codec=args.codec, crf=args.crf, dry_run=args.dry_run)
