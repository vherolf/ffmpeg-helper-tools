#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
from common import get_logger

logger = get_logger(__name__)

video_dir = Path(Path.cwd(), 'videos')
image_dir = Path(Path.cwd(), 'images')

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

# name used in the filename -> (background color for ffmpeg and pillow, font color)
COLORS = {
    'blue': ('blue', 'white'),
    'green': ('green', 'white'),
    'white': ('white', 'black'),
    'red': ('red', 'white'),
    'pink': ('pink', 'black'),
    'darkgrey': ('#404040', 'white'),
}

# video lengths in seconds
DURATIONS = [30, 60]

# video and image heights in pixels, the width follows at 16:9 (720 -> 1280x720)
RESOLUTIONS = [720]

# digits drawn on the test images
DIGITS = range(7)

# test input for the other scripts, short is enough
TOOL_TEST_DURATION = 10

# mosaic.py / mosaic-left-right.py: one folder per pair with exactly 2 videos, <pair>_left.mp4 and <pair>_right.mp4
MOSAIC_PAIRS = [('blue', 'green'), ('red', 'white'), ('pink', 'darkgrey')]

# videoslicer-*.py: scene colors and how the scenes are put together
SLICER_SCENES = {
    'horizontal': (['blue', 'green', 'red'], 'hstack'),  # 3 scenes side by side, e.g. 3840x720
    'vertical': (['blue', 'green'], 'vstack'),           # 2 scenes stacked, e.g. 1280x720
}

# background tune: semitones above the base note, one per half second, None is a rest
# C E G C G E C (rest) - a 4 second loop, one note lands on every full second of the counter
MELODY = [0, 4, 7, 12, 7, 4, 0, None]

def encoder_args(codec='x264', crf=None):
    if crf is None:
        crf = CODECS[codec]['crf']
    return CODECS[codec]['args'] + ['-crf', str(crf), '-pix_fmt', 'yuv420p']

# 16:9 width for a height, rounded to an even number for yuv420p
def width_for(height=720):
    return round(height * 16 / 9 / 2) * 2

def codec_dir(codec='x264'):
    out = CODECS[codec]['dir']
    out.mkdir(parents=True, exist_ok=True)
    return out

# write text in the middle of the image, the font scales with the height (700 at 720p)
def generate_test_image(name='white', text=u'1', height=720, fontcolor='black', backgroundcolor='white', image_dir=image_dir):
    image_dir.mkdir(parents=True, exist_ok=True)
    width = width_for(height)
    fontsize = height * 700 // 720
    font = ImageFont.truetype("FreeMono.ttf", fontsize, encoding="unic")
    canvas = Image.new('RGB', (width, height), backgroundcolor)
    draw = ImageDraw.Draw(canvas)
    # use anchor="mm" for center in middle (THANK YOU STACK OVERFLOW)
    draw.text((width/2, height/2), text, fontcolor, font, anchor="mm")
    out = Path(image_dir, f'{name}{text}-{height}p.png')
    canvas.save(out, "PNG")
    logger.info('generated image %s', out)
    return out

# drawtext filter that shows the current frame number at the bottom of the video
def frame_number_filter(fontcolor='white', fontsize=50):
    fontfile = ImageFont.truetype("FreeMono.ttf", fontsize).path
    return (f"drawtext=fontfile={fontfile}:fontsize={fontsize}:fontcolor={fontcolor}"
            r":text='frame %{n}'"
            ":x=(w-text_w)/2:y=h-text_h-h/36")

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

# filter chain for one solid color panel with a running seconds counter in the middle,
# the frame number below and an optional label on top, text scales with the height (500 at 720p)
def counter_panel(backgroundcolor='blue', fontcolor='white', width=1280, height=720, duration=30, framerate=25, label=None):
    fontsize = height * 500 // 720
    fontfile = ImageFont.truetype("FreeMono.ttf", fontsize).path
    parts = [f'color=c={backgroundcolor}:s={width}x{height}:r={framerate}:d={duration}',
             (f"drawtext=fontfile={fontfile}:fontsize={fontsize}:fontcolor={fontcolor}"
              r":text='%{eif\:t\:d}'"
              ":x=(w-text_w)/2:y=(h-text_h)/2"),
             frame_number_filter(fontcolor, fontsize // 10)]
    if label:
        parts.append(f"drawtext=fontfile={fontfile}:fontsize={fontsize // 10}:fontcolor={fontcolor}"
                     f":text='{label}':x=(w-text_w)/2:y=h/36")
    return ','.join(parts)

# encode one or more panels (stacked with hstack or vstack) with a quiet looping tune
# (peaks around -24 dBFS) as audio
def encode_video(outputname, panels, stack='hstack', duration=30, volume=0.06, crf=None, codec='x264'):
    outputname.parent.mkdir(parents=True, exist_ok=True)
    logger.info('generating video %s', outputname)
    graph = ';'.join(f'{panel}[p{i}]' for i, panel in enumerate(panels))
    graph += ';' + ''.join(f'[p{i}]' for i in range(len(panels))) + (f'{stack}=inputs={len(panels)}[v]' if len(panels) > 1 else 'null[v]')
    subprocess.run([FFMPEG,
                    '-f', 'lavfi',
                    '-i', f"aevalsrc='{melody_expression(volume=volume)}':s=48000:d={duration}",
                    '-filter_complex', graph,
                    '-map', '[v]', '-map', '0:a',
                    *encoder_args(codec, crf),
                    '-c:a', 'aac', '-b:a', '128k',
                    '-shortest',
                    outputname, '-y'], check=True)

# solid color counter video <color>-<duration>-<height>p.mp4
def generate_counter_video(name='blue', height=720, duration=30, crf=None, codec='x264'):
    backgroundcolor, fontcolor = COLORS[name]
    outputname = Path(codec_dir(codec), f'{name}-{duration}-{height}p.mp4')
    encode_video(outputname, [counter_panel(backgroundcolor, fontcolor, width_for(height), height, duration)],
                 duration=duration, crf=crf, codec=codec)

# input for mosaic.py and mosaic-left-right.py: mosaic/<left>-<right>-<height>p/ with exactly 2 videos
def generate_mosaic_pair(left='blue', right='green', height=720, duration=TOOL_TEST_DURATION, crf=None, codec='x264'):
    pair = f'{left}-{right}-{height}p'
    for side, name in (('left', left), ('right', right)):
        backgroundcolor, fontcolor = COLORS[name]
        outputname = Path(codec_dir(codec), 'mosaic', pair, f'{pair}_{side}.mp4')
        encode_video(outputname, [counter_panel(backgroundcolor, fontcolor, width_for(height), height, duration)],
                     duration=duration, crf=crf, codec=codec)

# input for videoslicer-horizontal.py (3 scenes side by side) and videoslicer-vertical.py (2 scenes stacked)
# the slicers need the filename format "YYYY-MM-DD HH-MM-SS.mp4": the year is the resolution and the time
# the video length (0720-01-01 00-00-10.mp4), so every resolution slices into its own output folder
def generate_slicer_video(direction='horizontal', height=720, duration=TOOL_TEST_DURATION, crf=None, codec='x264'):
    names, stack = SLICER_SCENES[direction]
    width = width_for(height)
    panelheight = height if stack == 'hstack' else height // 4 * 2
    panels = [counter_panel(*COLORS[name], width, panelheight, duration, label=f'scene {i + 1}')
              for i, name in enumerate(names)]
    length = f'{duration // 3600:02}-{duration // 60 % 60:02}-{duration % 60:02}'
    outputname = Path(codec_dir(codec), f'videoslicer-{direction}', f'{height}p', f'{height:04}-01-01 {length}.mp4')
    encode_video(outputname, panels, stack=stack, duration=duration, crf=crf, codec=codec)

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
    parser.add_argument("--resolution", nargs='+', type=int, default=RESOLUTIONS,
                        help=f"heights in pixels, width is 16:9, e.g. 720 1080 2160 (default: {' '.join(map(str, RESOLUTIONS))})")
    parser.add_argument("--images-only", default=False, action="store_true",
                        help="only generate the test images in images/, no videos")
    args = parser.parse_args()

    # list fonts available and exit
    if args.list_fonts_available:
        list_font_families()
        exit()

    # default behaviour without any commandline options
    # generates <color><digit>-<height>p.png test images for every color and resolution
    for height in args.resolution:
        for name in args.color:
            backgroundcolor, fontcolor = COLORS[name]
            for digit in DIGITS:
                generate_test_image(name, f'{digit}', height=height, fontcolor=fontcolor, backgroundcolor=backgroundcolor)
    if args.images_only:
        exit()

    # and <color>-<duration>-<height>p.mp4 for every codec, resolution, color and duration
    # plus short test input for the mosaic and videoslicer scripts
    for codec in args.codec:
        for height in args.resolution:
            for duration in args.duration:
                for name in args.color:
                    generate_counter_video(name, height=height, duration=duration, crf=args.crf, codec=codec)
            for left, right in MOSAIC_PAIRS:
                if left in args.color and right in args.color:
                    generate_mosaic_pair(left, right, height=height, crf=args.crf, codec=codec)
            for direction in SLICER_SCENES:
                generate_slicer_video(direction, height=height, crf=args.crf, codec=codec)
