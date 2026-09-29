import math
from pico2d import *


class CharacterAnimator:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        open_canvas(self.width, self.height)
        self.character = load_image('character.png')
        
        self.cx, self.cy = 400, 300
        self.radius = 200
        
        self.frame_delay = 0.01
        self.circle_steps = 2
        self.line_steps = 60
        
        self.rect_points = [(100, 100), (700, 100), (700, 500), (100, 500)]
        self.tri_points = [(100, 100), (700, 100), (400, 500)]

    def render(self, x, y):
        clear_canvas()
        self.character.draw(x, y)
        update_canvas()
        get_events()
        delay(self.frame_delay)

    def draw_path(self, path_points):
        total_points = len(path_points)
        for idx in range(total_points):
            start_p = path_points[idx]
            end_p = path_points[(idx + 1) % total_points]
            
            for step in range(self.line_steps + 1):
                ratio = step / self.line_steps
                curr_x = start_p[0] + (end_p[0] - start_p[0]) * ratio
                curr_y = start_p[1] + (end_p[1] - start_p[1]) * ratio
                self.render(curr_x, curr_y)

    def draw_circle(self):
        print("CIRCLE")
        for angle in range(0, 360, self.circle_steps):
            rad = math.radians(angle)
            curr_x = self.cx + self.radius * math.cos(rad)
            curr_y = self.cy + self.radius * math.sin(rad)
            self.render(curr_x, curr_y)

    def draw_rectangle(self):
        print("RECTANGLE")
        self.draw_path(self.rect_points)

    def draw_triangle(self):
        print("TRIANGLE")
        self.draw_path(self.tri_points)

    def run(self):
        try:
            while True:
                self.draw_circle()
                self.draw_rectangle()
                self.draw_triangle()
        except Exception as err:
            print(f"Animation stopped: {err}")
        finally:
            close_canvas()


if __name__ == '__main__':
    animator = CharacterAnimator()
    animator.run()