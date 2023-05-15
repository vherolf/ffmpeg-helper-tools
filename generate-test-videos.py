import subprocess
from pathlib import Path

FFMPEG = 'ffmpeg'

def generate_video_from_one_image(image=None, width=1280, height=720, duration=30):
    outputname = Path(image).stem + '.mp4'
    subprocess.call([FFMPEG, 
                     '-loop', '1', 
                     '-i', image, 
                     '-c:v', 'libx264', 
                     '-t', f'{duration}', 
                     '-pix_fmt', 'yuv420p', 
                     '-vf', f"scale={width}:{height}",
                     outputname, '-y' ])

if __name__=='__main__':
    generate_video_from_one_image('1.png')

