from vector import Vector
import polygon
import mapgen
import pyglet
import math
from car import ROYAL_COLOR

class PresidentNotice:
    def __init__(self, game, text, color):
        self.time = 0
        self.game = game
        x1 = 0
        y1 = self.game.window.height * (4/8)
        x2 = self.game.window.width
        y2 = self.game.window.height * (4/8)
        self.color = color
        self.background = polygon.Polygon(
            0,0,
            [Vector(x1,y1), Vector(x2,y1), Vector(x2, y2), Vector(x1,y2)],
            (*self.color, 0),1, game.batches['guitop'],
            pyglet.gl.GL_POLYGON)
        self.text = pyglet.text.Label(
            text,
            font_name="Menlo", font_size=30, anchor_x="center", anchor_y="center",
            bold=True,
            color=(255,255,255,255),
            batch=self.game.batches['guitoptext'],
            x = - 400,
            y = y2 / 2 + 174,
        )
        self.text_velocity = 300
        self.tx = self.text.x

    def update(self, delta_time):
        self.time += delta_time
        if self.time <= 1.5:
            self.background.color = (*self.color, min(int(self.time * 500), 255))

            z = math.cos(min(self.time * 3.14159,3.14159)) * -35 + 35
            x1 = 0
            y1 = self.game.window.height /2 - z
            x2 = self.game.window.width
            y2 = self.game.window.height /2 + z
            self.background.set_points([Vector(x1,y1), Vector(x2,y1), Vector(x2, y2), Vector(x1,y2)])

        elif self.time <= 6:
            self.tx += self.text_velocity * delta_time
            self.text.x = int(self.tx)
            pt1 = self.game.window.width / 2 - 40
            pt2 = self.game.window.width / 2 + 40
            if self.text.x < pt1:
                self.text_velocity = (pt1 - self.text.x) * 8 + 30
            elif self.text.x < pt2:
                self.text_velocity = 30
            else:
                self.text_velocity += 10000 * delta_time
        else:
            self.background.color = (*self.color, max(min(int((7 - self.time) * 255), 255), 0))

            z = (7 - self.time) * 70
            x1 = 0
            y1 = self.game.window.height /2 - z
            x2 = self.game.window.width
            y2 = self.game.window.height /2 + z
            self.background.set_points([Vector(x1,y1), Vector(x2,y1), Vector(x2, y2), Vector(x1,y2)])
