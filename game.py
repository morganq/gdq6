import pyglet
from collections import OrderedDict
from level import Level
import pyttsx3
import player


class Game:
    def __init__(self, window):
        self.window = window
        self.batches = OrderedDict()
        self.speaker = pyttsx3.init()
        self.speaker.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
        self.playercontrol = None
        self.scene = []

    def draw(self):
        pyglet.gl.glClearColor( 1.0, 0.98, 0.9, 1.0 )
        self.window.clear()
        pyglet.gl.glEnable( pyglet.gl.GL_LINE_SMOOTH )
        pyglet.gl.glEnable( pyglet.gl.GL_POLYGON_SMOOTH )
        pyglet.gl.glHint( pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_NICEST )
        pyglet.gl.glHint( pyglet.gl.GL_POLYGON_SMOOTH_HINT, pyglet.gl.GL_NICEST )
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glLineWidth(2)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        for batch in self.batches.values():
            batch.draw()

    def update(self, delta_time):
        for obj in self.scene:
            obj.update(delta_time)
        self.level.update(delta_time)
        self.playercontrol.update(delta_time)
        self.speaker.iterate()

    def run(self):
        self.batches['map'] = pyglet.graphics.Batch()
        self.batches['foreground'] = pyglet.graphics.Batch()
        self.batches['gui'] = pyglet.graphics.Batch()

        self.playercontrol = player.PlayerControl(self)

        self.window.on_draw = self.draw
        self.window.on_mouse_motion = self.playercontrol.mousemove
        self.window.on_mouse_press = self.playercontrol.mousepress
        self.window.on_mouse_release = self.playercontrol.mouserelease
        self.window.on_mouse_drag = self.playercontrol.mousedrag

        self.level = Level(self, 1)
        self.scene = self.level.create()
        pyglet.clock.schedule(self.update)
        self.speaker.startLoop(False)
        self.window.activate()
        pyglet.app.run()