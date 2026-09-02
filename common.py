import logging
import os
from pathlib import Path

import ffmpeg

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
