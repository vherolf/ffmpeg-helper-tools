import logging
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

def is_video(filename):
    try:
        probe = ffmpeg.probe(filename)
        return any(s['codec_type'] == 'video' for s in probe['streams'])
    except ffmpeg.Error as e:
        get_logger(__name__).warning('ffprobe failed for %s: %s', filename, e)
        return False
