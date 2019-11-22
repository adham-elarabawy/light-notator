# author: Adham Elarabawy
from p5 import *
from tkinter import Tk
from scipy.spatial import distance
import PIL
from PIL import Image
import argparse
import os
import mimetypes


parser = argparse.ArgumentParser(
    description='Custom frame annotator implemented in p5 and python.')
parser.add_argument('--input', dest='input',
                    help='Path to the directory with the input images', required=False, type=str, default='input/'),
parser.add_argument('--output', dest='output',
                    help='Path to the directory with the output images', required=False, type=str, default='output/'),
parser.add_argument('--cache', dest='cache',
                    help='Path to the cache directory (DON\'T INCLUDE \\)', required=False, type=str, default='cache'),
parser.add_argument('--scale', dest='scale',
                    help='scaling factor for viewing images', required=False, type=float, default=0.3),

# -- CONFIG -- #
root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

image_width = width - 200
image_height = (height/width) * image_width

args = parser.parse_args()

input_dir = args.input
output_dir = args.output

dirs = []
images = []
index = 0

points = []
last_action = 'script started'


def load():
    global last_action
    load_images_from_folder(input_dir)
    last_action = 'loaded images'


def setup():
    global last_action
    size(width, image_height)
    title('Light-notator')
    last_action = 'setup window'
    no_loop()


def draw():
    global dirs, images, index, points
    load_pixels()
    background(255)
    if index > len(images) - 1:
        index = 0
    if index < 0:
        index = len(images) - 1

    image(images[index], (0, 0), (image_width, image_height))
    text(f'index: {index}', (5, 5))
    text(f'current image: ({dirs[index]})', (5, 15))
    text(f'last action: ({last_action})', (5, 25))

    for point in points:
        ellipse((point[0], point[1]), 5, 5)


def mouse_pressed():
    global points, last_action
    print(f'mouse pressed at ({mouse_x},{mouse_y})')
    if mouse_x <= image_width and mouse_y <= image_height:
        points.append((mouse_x, mouse_y))
        last_action = 'added point'
    redraw()


def key_pressed():
    global points, last_action, index
    if ((key == 'R') or (key == 'r')):
        curr_pos = (mouse_x, mouse_y)
        dist = []
        for point in points:
            dist.append(distance.euclidean(point, curr_pos))
        points.pop(dist.index(min(dist)))
        last_action = 'removed closest point'
    if ((key == 'c') or (key == 'C')):
        points = []
        last_action = 'cleared all points'

    if (key == "2"):
        last_action = 'moved to next frame'
        index += 1
    if (key == "1"):
        last_action = 'moved to previous frame'
        index -= 1
    redraw()


def load_images_from_folder(folder):
    global dirs, images
    for filename in os.listdir(folder):
        img_dir = os.path.join(folder, filename)
        file_type = str(mimetypes.guess_type(img_dir)[0])[0:5]
        if file_type == 'image':
            temp_img = Image.open(img_dir)
            wsize = int((float(temp_img.size[0]) * float(args.scale)))
            hsize = int((float(temp_img.size[1]) * float(args.scale)))
            temp_img = temp_img.resize((wsize, hsize), PIL.Image.ANTIALIAS)
            new_dir = os.path.join(args.cache, filename)
            temp_img.save(f'{new_dir}')

            dirs.append(new_dir)
            images.append(load_image(new_dir))
    dirs, images = (list(t) for t in zip(*sorted(zip(dirs, images))))


if __name__ == '__main__':
    load()
    run()
