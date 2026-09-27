import logging
import os
from pathlib import Path

import ffmpeg

# browser compatible video codecs (chrome, firefox, edge, safari 17+), CPU encoding
# x264 is the default, av1 the second option; crf is the default quality per codec
VIDEO_CODECS = {
    'x264': {'args': ['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', '-movflags', '+faststart'],
             'crf': 23},
    'av1':  {'args': ['-c:v', 'libsvtav1', '-preset', '6', '-movflags', '+faststart'],
             'crf': 35},
}

def video_encoder_args(codec='x264', crf=None):
    if crf is None:
        crf = VIDEO_CODECS[codec]['crf']
    return VIDEO_CODECS[codec]['args'] + ['-crf', str(crf), '-pix_fmt', 'yuv420p']

# audio codecs that play in mp4 in all browsers are copied, everything else
# (pcm, ac3, e-ac3, dts, flac, opus, ...) is converted to aac
BROWSER_AUDIO_CODECS = ('aac', 'mp3')

def audio_encoder_args(filename):
    try:
        streams = [s for s in ffmpeg.probe(filename)['streams'] if s['codec_type'] == 'audio']
    except ffmpeg.Error:
        streams = []
    if all(s['codec_name'] in BROWSER_AUDIO_CODECS for s in streams):
        return ['-c:a', 'copy']
    channels = max(s.get('channels', 2) for s in streams)
    return ['-c:a', 'aac', '-b:a', '192k' if channels <= 2 else '384k']

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)-8s %(name)s — %(message)s',
            datefmt='%H:%M:%S'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def add_file_handler(logger, path):
    handler = logging.FileHandler(path)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)-8s %(name)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

def is_video(filename):
    try:
        probe = ffmpeg.probe(filename)
        format_name = probe.get('format', {}).get('format_name', '')
        if format_name == 'image2' or format_name == 'gif' or format_name.endswith('_pipe'):
            return False
        return any(s['codec_type'] == 'video' for s in probe['streams'])
    except ffmpeg.Error as e:
        get_logger(__name__).warning('ffprobe failed for %s: %s', filename, e)
        return False

def iter_files(source):
    for root, dirs, files in os.walk(source):
        for file in files:
            yield root, file

def iter_videos(source):
    for root, file in iter_files(source):
        if is_video(Path(root, file)):
            yield root, file
