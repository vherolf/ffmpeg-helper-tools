#!/usr/bin/env python

from PIL import ImageFont
from pathlib import Path
import subprocess
from common import get_logger

logger = get_logger(__name__)

video_dir = Path(Path.cwd(), 'videos')

FFMPEG = 'ffmpeg'

# output subfolder, encoder options and default crf per codec
# both are browser compatible (chrome, firefox, edge, safari 17+)
CODECS = {
    'x264': {'dir': Path(video_dir, 'x264'),
             'args': ['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', '-movflags', '+faststart'],
             'crf': 23},
    'av1':  {'dir': Path(video_dir, 'av1'),
             'args': ['-c:v', 'libsvtav1', '-preset', '6', '-movflags', '+faststart'],
             'crf': 35},
}

# name used in the filename -> (ffmpeg background color, font color)
COLORS = {
    'blue': ('blue', 'white'),
    'green': ('green', 'white'),
    'white': ('white', 'black'),
    'red': ('red', 'white'),
    'pink': ('pink', 'black'),
    'darkgrey': ('0x404040', 'white'),
}

# video lengths in seconds
DURATIONS = [30, 60]

# background tune: semitones above the base note, one per half second, None is a rest
# C E G C G E C (rest) - a 4 second loop, one note lands on every full second of the counter
MELODY = [0, 4, 7, 12, 7, 4, 0, None]

def encoder_args(codec='x264', crf=None):
    if crf is None:
        crf = CODECS[codec]['crf']
    return CODECS[codec]['args'] + ['-crf', str(crf), '-pix_fmt', 'yuv420p']

def codec_dir(codec='x264'):
    out = CODECS[codec]['dir']
    out.mkdir(parents=True, exist_ok=True)
    return out

# drawtext filter that shows the current frame number at the bottom of the video
def frame_number_filter(fontcolor='white', fontsize=50):
    fontfile = ImageFont.truetype("FreeMono.ttf", fontsize).path
    return (f"drawtext=fontfile={fontfile}:fontsize={fontsize}:fontcolor={fontcolor}"
            r":text='frame %{n}'"
            ":x=(w-text_w)/2:y=h-text_h-20")

# aevalsrc expression for a soft plucked tune that loops the MELODY
# every note is a sine plus a quiet octave, with a quick fade in and an exponential fade out
def melody_expression(melody=MELODY, basefrequency=261.63, notelength=0.5, volume=0.06):
    slot = f'mod(floor(t/{notelength}),{len(melody)})'
    notetime = f'mod(t,{notelength})'
    semitones = '0'
    for i, semitone in reversed(list(enumerate(melody))):
        if semitone is not None:
            semitones = f'if(eq({slot},{i}),{semitone},{semitones})'
    playing = '*'.join(f'not(eq({slot},{i}))' for i, semitone in enumerate(melody) if semitone is None) or '1'
    frequency = f'{basefrequency}*pow(2,({semitones})/12)'
    envelope = f'(1-exp(-300*{notetime}))*exp(-7*{notetime})*(1-{notetime}/{notelength})'
    tone = f'(sin(2*PI*{frequency}*{notetime})+0.3*sin(4*PI*{frequency}*{notetime}))'
    return f'{volume}*{playing}*{envelope}*{tone}'

# solid color video with a running seconds counter in the middle and the frame number below
# plus a quiet looping tune (peaks around -22 dBFS) as audio
def generate_counter_video(name='blue', backgroundcolor='blue', fontcolor='white', width=1280, height=720, duration=30, framerate=25, fontsize=500, volume=0.06, crf=None, codec='x264'):
    outputname = Path(codec_dir(codec), f'{name}-{duration}.mp4')
    fontfile = ImageFont.truetype("FreeMono.ttf", fontsize).path
    logger.info('generating counter video %s', outputname)
    counter = (f"drawtext=fontfile={fontfile}:fontsize={fontsize}:fontcolor={fontcolor}"
               r":text='%{eif\:t\:d}'"
               ":x=(w-text_w)/2:y=(h-text_h)/2")
    frame = frame_number_filter(fontcolor, fontsize // 10)
    subprocess.run([FFMPEG,
                    '-f', 'lavfi',
                    '-i', f'color=c={backgroundcolor}:s={width}x{height}:r={framerate}:d={duration}',
                    '-f', 'lavfi',
                    '-i', f"aevalsrc='{melody_expression(volume=volume)}':s=48000:d={duration}",
                    *encoder_args(codec, crf),
                    '-vf', f'{counter},{frame}',
                    '-c:a', 'aac', '-b:a', '128k',
                    '-shortest',
                    outputname, '-y'], check=True)

def list_font_families():
    from tkinter import Tk, font
    root = Tk()
    print( font.families() )

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list-fonts-available", default=False, action="store_true")
    parser.add_argument("-c", "--crf", type=int, default=None,
                        help="crf for all codecs (default: x264 23, av1 35)")
    parser.add_argument("--codec", nargs='+', choices=list(CODECS), default=list(CODECS),
                        help="codecs to generate: x264 -> videos/x264/, av1 -> videos/av1/ (default: all)")
    parser.add_argument("--color", nargs='+', choices=list(COLORS), default=list(COLORS),
                        help="background colors to generate (default: all)")
    parser.add_argument("--duration", nargs='+', type=int, default=DURATIONS,
                        help=f"video lengths in seconds (default: {' '.join(map(str, DURATIONS))})")
    args = parser.parse_args()

    # list fonts available and exit
    if args.list_fonts_available:
        list_font_families()
        exit()

    # default behaviour without any commandline options
    # generates <color>-<duration>.mp4 for every codec, color and duration
    for codec in args.codec:
        for duration in args.duration:
            for name in args.color:
                backgroundcolor, fontcolor = COLORS[name]
                generate_counter_video(name, backgroundcolor, fontcolor, duration=duration, crf=args.crf, codec=codec)
