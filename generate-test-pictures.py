from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import subprocess

# write text in the middle of the image
def generate_test_image(text=u'1', width=1280, height=720, fontsize=700, fontcolor='black',backgroundcolor='white'):
    font = ImageFont.truetype("FreeMono.ttf", fontsize, encoding="unic")
    #textlength = font.getlength(text)
    #bbox = font.getbbox(text)
    canvas = Image.new('RGB', (width, height), backgroundcolor)
    draw = ImageDraw.Draw(canvas)
    # use anchor="mm" for center in middle (THANK YOU STACK OVERFLOW)
    draw.text((width/2, height/2), text, fontcolor, font, anchor="mm")
    canvas.save( text +".png", "PNG")
    #canvas.show()



if __name__=='__main__':
    for text in range(20):
        generate_test_image( f'{text}' )