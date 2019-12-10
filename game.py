import pyglet
from collections import OrderedDict
import level

class Game:
    def __init__(self, window):
        self.window = window
        self.batches = OrderedDict()
        self.scene = []

    def draw(self):
        for batch in self.batches.values():
            batch.draw()

    def update(self, delta_time):
        for obj in self.scene:
            obj.update(delta_time)

    def run(self):
        self.window.on_draw = self.draw
        self.scene = level.create_scene(self)
        pyglet.clock.schedule(self.update)
        pyglet.app.run()