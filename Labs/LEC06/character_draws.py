# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

cx, cy = 400, 300
radius = 200

FRAME_DELAY = 0.01
CIIRCLE_STEPS = 2
LINE_STEPS = 60

rect_p1 = (100, 100)
rect_p2 = (700, 100)
rect_p3 = (700, 500)
rect_p4 = (100, 500)

tri_p1 = (100, 100)
tri_p2 = (700, 100)
tri_p3 = (400, 500)

def render_character(x, y):
    clear_canvas()
    character.draw(x, y)
    update_canvas()
    get_events()
    delay(FRAME_DELAY)

def move_along_line(p1, p2, steps=LINE_STEPS):
    x1, y1 = p1
    x2, y2 = p2
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        render_character(x, y)

def move_circle():
    print("CIRCLE")
    for deg in range(0, 360, CIIRCLE_STEPS):
        rad = math.radians(deg)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        render_character(x, y)

def move_rectangle():
    print("RECTANGLE")
    move_along_line(rect_p1, rect_p2)
    move_along_line(rect_p2, rect_p3)
    move_along_line(rect_p3, rect_p4)
    move_along_line(rect_p4, rect_p1)
    
def move_triangle():
    print("TRIANGLE")
    move_along_line(tri_p1, tri_p2)
    move_along_line(tri_p2, tri_p3)
    move_along_line(tri_p3, tri_p1)
    
while True:
    move_circle()
    move_rectangle()
    move_triangle()
    break

close_canvas()