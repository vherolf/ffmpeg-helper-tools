import ffmpeg

def is_video(filename):
    try:
        probe = ffmpeg.probe(filename)
        return any(s['codec_type'] == 'video' for s in probe['streams'])
    except ffmpeg.Error:
        return False
