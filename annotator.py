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
import csv
import mimetypes

DEBUG = False

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

window_offset = 200

image_width = width - window_offset
image_height = (height/width) * image_width

args = parser.parse_args()

input_dir = args.input
output_dir = args.output
cache_dir = args.cache

dirs = []
images = []
img_size = []
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


def validate_dirs():
    global DEBUG, input_dir, output_dir, cache_dir
    dir_list = [input_dir, output_dir, cache_dir]
    for directory in dir_list:
        if not os.path.exists(directory):
            os.makedirs(directory)
    if DEBUG:
        print('[validate_dirs] Validated Directories')


def load():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    validate_dirs()
    load_images_from_folder(input_dir)
    rectangles = load_bbox_from_file()
    last_action = 'loaded images'


def setup():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    size(width - window_offset, image_height)
    title('Light-notator')
    last_action = 'setup window'
    no_loop()
    rect_mode(mode='CENTER')


def check_index():
    global index
    if index > len(images) - 1:
        index = 0
    if index < 0:
        index = len(images) - 1


def draw():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    background(255)
    check_index()

    image(images[index], (0, 0), (image_width, image_height))

    text(f'index: {index}', (5, 5))
    text(f'current image: ({dirs[index]})', (5, 15))
    text(f'# points: {len(points)}', (5, 25))
    text(f'last action: ({last_action})', (5, 35))

    for m_rectangle in rectangles:
        no_fill()
        stroke_weight(2)
        stroke(117, 255, 117)
        x_translate = floor(m_rectangle[0] * img_size[index][0])
        y_translate = floor(m_rectangle[1] * img_size[index][1])
        rect_width = floor(m_rectangle[2] * img_size[index][0])
        rect_height = floor(m_rectangle[3] * img_size[index][1])
        translate(x_translate, y_translate)
        rotate(m_rectangle[4])
        rect((0, 0), rect_width, rect_height)
        rotate(-1 * m_rectangle[4])
        translate(-1 * x_translate, -1 * y_translate)
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
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if DEBUG:
        print(f'mouse pressed at ({mouse_x},{mouse_y})')
    add_point(mouse_x, mouse_y, std_color)
    constrain_square()
    redraw()


def key_pressed():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
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
        write_bbox_to_file()
        index += 1
        check_index()
        rectangles = load_bbox_from_file()
    if (key == "1"):
        last_action = 'moved to previous frame'
        write_bbox_to_file()
        index -= 1
        check_index()
        rectangles = load_bbox_from_file()
    redraw()


def load_images_from_folder(folder):
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
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

            img_size.append((image_width, image_height))
            dirs.append(new_dir)
            images.append(load_image(new_dir))
    dirs, images, img_size = (list(t)
                              for t in zip(*sorted(zip(dirs, images, img_size))))


def add_point(in_x, in_y, color):
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if in_x <= image_width and in_y <= image_height:
        points.append((in_x, in_y))
        p_colors.append(color)
        last_action = 'added point'


def add_line(temp_point_0, temp_point_1, color):
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    lines.append((temp_point_0, temp_point_1))
    l_colors.append(Color(0, 0, 0))


def constrain_square():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    if len(points) == 3:
        dist = []
        pairs = []
        for pointA in points:
            for pointB in points:
                dist.append(abs(distance.euclidean(pointA, pointB)))
                pairs.append((pointA, pointB))

        for point in points:
            # arbitrarily define temporary points in order to find pointC
            if not ((point == pairs[dist.index(max(dist))][0]) or (point == pairs[dist.index(max(dist))][1])):
                pointC = point

        hypot = max(dist)
        temp_distance_0 = abs(distance.euclidean(
            pointC, pairs[dist.index(max(dist))][0]))
        temp_distance_1 = abs(distance.euclidean(
            pointC, pairs[dist.index(max(dist))][1]))
        if (temp_distance_0 > temp_distance_1):
            pointA = pairs[dist.index(max(dist))][0]
            pointB = pairs[dist.index(max(dist))][1]
            angle_flip = False
        else:
            pointA = pairs[dist.index(max(dist))][1]
            pointB = pairs[dist.index(max(dist))][0]
            angle_flip = True

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
        angle_factor = -1

        rectangle_tilt = get_angle([pointC[0], pointC[1]], [pointA[0], pointA[1]], [
            pointA[0] + 20, pointA[1]])
        if DEBUG:
            print(f'rectangle tilt is: {180 * rectangle_tilt / mp.pi}')

        rectangle_tilt *= angle_factor

        if DEBUG:
            print(f'shifted rectangle tilt is: {180 * rectangle_tilt / mp.pi}')

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
        points = []

    else:
        last_action = 'constrain_square failed: not enough points'
        lines = []


def add_rectangle(in_x, in_y, rectangle_width, rectangle_height, rectangle_tilt):
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    x_relative = in_x/img_size[index][0]
    y_relative = in_y/img_size[index][1]
    rect_width_relative = rectangle_width/img_size[index][0]
    rect_height_relative = rectangle_height/img_size[index][1]
    rectangles.append((x_relative, y_relative, rect_width_relative,
                       rect_height_relative, rectangle_tilt))


def validate_constraint():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
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
    if DEBUG:
        print(f'validated constraints: corner angles are {angles[0:4]}')


def get_angle(pointA, pointB, pointC):
    v1 = [pointA[0] - pointB[0], pointA[1] - pointB[1]]
    v2 = [pointC[0] - pointB[0], pointC[1] - pointB[1]]

    angle = np.arccos(
        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    if pointA[1] > pointC[1]:
        angle *= -1

    return angle


def remove_point():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    curr_pos = (mouse_x, mouse_y)
    dist = []
    for point in points:
        dist.append(distance.euclidean(point, curr_pos))
    points.pop(dist.index(min(dist)))
    last_action = 'removed closest point'
    constrain_square()


def load_bbox_from_file():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    file_dir = dirs[index].replace('cache', 'input')
    file_dir = os.path.splitext(file_dir)[0]+'.csv'
    if os.path.isfile(file_dir):
        temp_rectangles = []
        if DEBUG:
            print('There are encoded annotations in corresponding text file.')
        with open(file_dir) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                temp_rectangles.append(
                    (float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4])))
        return temp_rectangles
    else:
        if DEBUG:
            print('There are no encoded annotations in corresponding text file.')
        return []


def write_bbox_to_file():
    global DEBUG, last_action, points, dirs, images, img_size, index, input_dir, output_dir, args, width, height, image_width, image_height, lines, p_colors, l_colors, a_color, b_color, c_color, rectangles
    file_dir = dirs[index].replace('cache', 'input')
    file_dir = os.path.splitext(file_dir)[0]+'.csv'
    if os.path.isfile(file_dir):
        os.remove(file_dir)
    with open(file_dir, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for m_rectangle in rectangles:
            tmp_lst = [m_rectangle[0], m_rectangle[1],
                       m_rectangle[2], m_rectangle[3], m_rectangle[4]]
            filewriter.writerow(tmp_lst)


if __name__ == '__main__':
    load()
    run()
