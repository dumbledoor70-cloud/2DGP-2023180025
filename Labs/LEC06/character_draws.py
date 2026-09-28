# 실습 과제 진행
from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

cx, cy = 400, 300
radius = 200

def move_circle():
    print("CIRCLE")
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)

        clear_canvas()
        character.draw(x, y)
        update_canvas()
        delay(0.01)
    
def move_rectangle():
    print("RECTANGLE")
    pass
def move_triangle():
    print("TRIANGLE")
    pass

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    pass

close_canvas()