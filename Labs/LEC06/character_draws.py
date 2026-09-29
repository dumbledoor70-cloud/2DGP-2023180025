# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

cx, cy = 400, 300
radius = 200

rect_bottom, rect_top = 100, 500
rect_left, rect_right = 100, 700

tri_p1 = (100, 100)
tri_p2 = (700, 100)
tri_p3 = (400, 500)

def render_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)

def move_along_line(p1, p2, steps=50):
    x1, y1 = p1
    x2, y2 = p2
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        render_character(x, y)

def move_circle():
    print("CIRCLE")
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        render_character(x, y)

def rect_bottom_side():
    for x in range(rect_left, rect_right + 1, 10):
        render_character(x, rect_bottom)

def rect_right_side():
    for y in range(rect_bottom, rect_top + 1, 10):
        render_character(rect_right, y)

def rect_top_side():
    for x in range(rect_right, rect_left - 1, -10):
        render_character(x, rect_top)

def rect_left_side():
    for y in range(rect_top, rect_bottom - 1, -10):
        render_character(rect_left, y)

def move_rectangle():
    print("RECTANGLE")
    pass
def move_triangle():
    print("TRIANGLE")
    pass

move_along_line(tri_p1, tri_p2)
move_along_line(tri_p2, tri_p3)
move_along_line(tri_p3, tri_p1)

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass

close_canvas()