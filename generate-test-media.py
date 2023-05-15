from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

video_dir = Path(Path.cwd(), 'videos')
image_dir = Path(Path.cwd(), 'images')

FFMPEG = 'ffmpeg'

def list_font_families():
    from tkinter import Tk, font
    root = Tk()
    print( font.families() )

# write text in the middle of the image
def generate_test_image(text=u'1', width=1280, height=720, fontsize=700, fontcolor='black',backgroundcolor='white', image_dir=image_dir):
    font = ImageFont.truetype("FreeMono.ttf", fontsize, encoding="unic")
    canvas = Image.new('RGB', (width, height), backgroundcolor)
    draw = ImageDraw.Draw(canvas)
    # use anchor="mm" for center in middle (THANK YOU STACK OVERFLOW)
    draw.text((width/2, height/2), text, fontcolor, font, anchor="mm")
    canvas.save( Path(image_dir, f'{backgroundcolor}'+ text +".png"), "PNG")
    #canvas.show()

def generate_video_from_one_image(image=None, width=1280, height=720, duration=30, video_dir=video_dir):
    outputname = Path(video_dir, Path(image).stem + '.mp4')
    subprocess.call([FFMPEG, 
                     '-loop', '1', 
                     '-i', image, 
                     '-c:v', 'libx264', 
                     '-t', f'{duration}', 
                     '-pix_fmt', 'yuv420p', 
                     '-vf', f"scale={width}:{height}",
                     outputname, '-y' ])

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-l", "--list-fonts-available",default=False, action="store_true")
    parser.add_argument("-g", "--generate-media", default=True, action="store_true")
    args = parser.parse_args()

    if args.list_fonts_available:
        list_font_families()
        exit()

    if args.generate_media:
        for text in range(7):
            generate_test_image( f'{text}', fontcolor='black', backgroundcolor='white' )
            generate_test_image( f'{text}', fontcolor='white', backgroundcolor='blue' )
            generate_test_image( f'{text}', fontcolor='white', backgroundcolor='green' )
            
        for image in image_dir.glob('*.png'):
            generate_video_from_one_image(image)
