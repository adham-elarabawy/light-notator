# author: Adham Elarabawy
from p5 import *
import sympy as sym
import mpmath as mp
import numpy as np
from tkinter import Tk
from scipy.spatial import distance
import PIL
from PIL import Image
import argparse
import os
import mimetypes

DEBUG = True

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
c_points = []
lines = []
rectangles = []
p_colors = []
l_colors = []
last_action = 'script started'

std_color = Color(255, 255, 255)  # white
a_color = Color(255, 0, 0)  # azure
b_color = Color(0, 255, 0)  # rose
c_color = Color(0, 0, 255)  # pastel orange


def load():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    load_images_from_folder(input_dir)
    last_action = 'loaded images'


def setup():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    size(width, image_height)
    title('Light-notator')
    last_action = 'setup window'
    no_loop()
    rect_mode(mode='CENTER')


def draw():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    load_pixels()
    background(255)
    if index > len(images) - 1:
        index = 0
    if index < 0:
        index = len(images) - 1

    image(images[index], (0, 0), (image_width, image_height))
    text(f'index: {index}', (5, 5))
    text(f'current image: ({dirs[index]})', (5, 15))
    text(f'# points: {len(points)}', (5, 25))
    text(f'last action: ({last_action})', (5, 35))

    for m_rectangle in rectangles:
        no_fill()
        stroke_weight(2)
        stroke(117, 220, 117)
        translate(m_rectangle[0],
                  m_rectangle[1])
        rotate(m_rectangle[4])
        rect((0, 0), m_rectangle[2], m_rectangle[3])
        rotate(-1 * m_rectangle[4])
        translate(-1 * m_rectangle[0], -1 * m_rectangle[1])
    color_index = 0
    for m_point in points:
        fill(p_colors[color_index])
        stroke_weight(1)
        stroke(41)
        ellipse((m_point[0], m_point[1]), 5, 5)
        color_index += 1
    color_index = 0

    for m_line in lines:
        fill(l_colors[color_index])
        line(m_line[0], m_line[1])
        color_index += 1
    fill(std_color)


def mouse_pressed():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    print(f'mouse pressed at ({mouse_x},{mouse_y})')
    add_point(mouse_x, mouse_y, std_color)
    constrain_square()
    redraw()


def key_pressed():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if ((key == 'R') or (key == 'r')):
        remove_point()
    if ((key == 'c') or (key == 'C')):
        points = []
        lines = []
        rectangles = []
        p_colors = []
        l_colors = []
        last_action = 'cleared all points'
    if (key == 'd'):
        redraw()

    if (key == "2"):
        last_action = 'moved to next frame'
        index += 1
    if (key == "1"):
        last_action = 'moved to previous frame'
        index -= 1
    redraw()


def load_images_from_folder(folder):
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
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


def add_point(in_x, in_y, color):
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if in_x <= image_width and in_y <= image_height:
        points.append((in_x, in_y))
        p_colors.append(color)
        last_action = 'added point'


def add_line(temp_point_0, temp_point_1, color):
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    lines.append((temp_point_0, temp_point_1))
    l_colors.append(Color(0, 0, 0))


def constrain_square():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if len(points) == 3:
        dist = []
        pairs = []
        for pointA in points:
            for pointB in points:
                dist.append(abs(distance.euclidean(pointA, pointB)))
                pairs.append((pointA, pointB))

        hypot = max(dist)
        if (pairs[dist.index(max(dist))][0][1] < pairs[dist.index(max(dist))][1][1]) or ((pairs[dist.index(max(dist))][0][0] < pairs[dist.index(max(dist))][1][0])):
            pointA = pairs[dist.index(max(dist))][0]
            pointB = pairs[dist.index(max(dist))][1]
        else:
            pointA = pairs[dist.index(max(dist))][1]
            pointB = pairs[dist.index(max(dist))][0]
        for point in points:
            if not ((point == pointA) or (point == pointB)):
                pointC = point
            else:
                print('Constrain logic failed. Could not identify third point.')
        if DEBUG:
            p_colors[points.index(pointA)] = a_color
            p_colors[points.index(pointB)] = b_color
            p_colors[points.index(pointC)] = c_color
        leg1 = abs(distance.euclidean(pointC, pointA))

        hypot = abs(distance.euclidean(pointB, pointA))

        leg1_vector = (pointC[0] - pointA[0], pointC[1] - pointA[1])
        hypot_vector = (pointB[0] - pointA[0], pointB[1] - pointA[1])

        if DEBUG:
            add_line(pointA, pointB, std_color)
        print(
            f'leg vector is {leg1_vector} and hyp_vector is {hypot_vector}')
        print(
            f'pointA is {pointA} and pointB is {pointB} and pointC is {pointC}')
        theta = sym.acos(
            (leg1_vector[0]*hypot_vector[0]+leg1_vector[1]*hypot_vector[1])/(leg1*hypot))
        last_action = f'calculated theta = {theta}'
        print(last_action)

        std_unit_vector = (1, 0)
        theta_prime = sym.acos((leg1_vector[0]*std_unit_vector[0] +
                                leg1_vector[1]*std_unit_vector[1])/(leg1))
        leg2 = leg1 * mp.tan(theta)

        increment = (leg2 * mp.sin(theta_prime),
                     leg2 * mp.cos(theta_prime))

        temp_b_check = pointB[0] > pointA[0]

        if pointC[1] > pointA[1]:
            increment = (-1 * increment[0], increment[1])
        if not (temp_b_check == (float(pointC[0] + increment[0]) > pointA[0])):
            increment = (-1 * increment[0], -1 * increment[1])
        third_point = (float(pointC[0] + increment[0]),
                       float(pointC[1] + increment[1]))
        points[points.index(pointB)] = third_point
        pointB = third_point
        pointD = (float(pointA[0] + increment[0]),
                  float(pointA[1] + increment[1]))
        add_point(pointD[0], pointD[1], std_color)

        validate_constraint()
        angle_factor = 1
        if (pointC[0] < pointB[0]) and (pointC[1] < pointA[1]):
            angle_factor = -1

        rectangle_tilt = angle_factor * get_angle([pointC[0], pointC[1]], [pointA[0], pointA[1]], [
            pointA[0] + 20, pointA[1]])
        rectangle_width = abs(distance.euclidean(pointC, pointA))
        rectangle_height = abs(distance.euclidean(pointD, pointA))

        averageX = 0
        averageY = 0
        for point in points:
            averageX += point[0]
            averageY += point[1]
        averageX /= len(points)
        averageY /= len(points)
        add_rectangle(averageX, averageY, rectangle_width,
                      rectangle_height, rectangle_tilt)

    else:
        last_action = 'constrain_square failed: not enough points'
        lines = []


def add_rectangle(in_x, in_y, rectangle_width, rectangle_height, rectangle_tilt):
    rectangles.append((in_x, in_y, rectangle_width,
                       rectangle_height, rectangle_tilt))


def validate_constraint():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    angles = []
    for pointA in points:
        for pointB in points:
            if pointB == pointA:
                continue
            for pointC in points:
                if pointC == pointA or pointC == pointB:
                    continue
                angle = 180 * get_angle(pointA, pointB, pointC) / np.pi
                if angle == 90 or (angle > 89.9 and angle < 90.1):
                    angles.append(angle)
    print(f'validated constraints: corner angles are {angles}')


def get_angle(pointA, pointB, pointC):
    v1 = [pointA[0] - pointB[0], pointA[1] - pointB[1]]
    v2 = [pointC[0] - pointB[0], pointC[1] - pointB[1]]

    angle = np.arccos(
        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    return angle


def remove_point():
    global DEBUG, last_action, points, dirs, images, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    curr_pos = (mouse_x, mouse_y)
    dist = []
    for point in points:
        dist.append(distance.euclidean(point, curr_pos))
    points.pop(dist.index(min(dist)))
    last_action = 'removed closest point'
    constrain_square()


if __name__ == '__main__':
    load()
    run()
