import pyglet
from collections import OrderedDict
from level import Level
import player
import sound


class Game:
    def __init__(self, window):
        self.window = window
        self.batches = OrderedDict()
        self.playercontrol = None
        self.scene = []
        self.sound = sound.Sound(self)
        self.time = 0
        self._first_update = 0

    def draw(self):
        pyglet.gl.glClearColor( 241 / 255, 237 / 255, 216/255, 0.0 )
        self.window.clear()
        pyglet.gl.glEnable( pyglet.gl.GL_LINE_SMOOTH )
        pyglet.gl.glEnable( pyglet.gl.GL_POLYGON_SMOOTH )
        pyglet.gl.glHint( pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_NICEST )
        pyglet.gl.glHint( pyglet.gl.GL_POLYGON_SMOOTH_HINT, pyglet.gl.GL_NICEST )
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        #pyglet.gl.glLineWidth(2)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        for batch in self.batches.values():
            batch.draw()

    def pass_event_to(self, fn):
        def exception_catch_handler(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                print(e)
        return exception_catch_handler

    def key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            if self.level and self.level.tut:
                self.level.tut.hide()
                self.level.tut.messages = []
            return pyglet.event.EVENT_HANDLED

    def update(self, delta_time):
        delta_time = min(delta_time, 0.1)
        self.time += delta_time
        if self._first_update == 2:
            self.playercontrol = player.PlayerControl(self)

            self.window.on_draw = self.draw
            self.window.on_key_press = self.key_press
            self.window.on_mouse_motion = self.pass_event_to(self.playercontrol.mousemove)
            self.window.on_mouse_press = self.pass_event_to(self.playercontrol.mousepress)
            self.window.on_mouse_release = self.pass_event_to(self.playercontrol.mouserelease)
            self.window.on_mouse_drag = self.pass_event_to(self.playercontrol.mousedrag)
            self.level = Level(self, 1)
            self.scene = self.level.create()    
            m = self.sound.music.play()
            m.loop = True
        
        self._first_update += 1

        if self._first_update > 2:
            for obj in self.scene:
                obj.update(delta_time)
            self.level.update(delta_time)
            self.playercontrol.update(delta_time)

    def set_cursor(self, cursor):
        self.window.set_mouse_cursor(self.window.get_system_mouse_cursor(cursor))

    def run(self):
        self.batches['map'] = pyglet.graphics.Batch()
        self.batches['path'] = pyglet.graphics.Batch()
        self.batches['foreground'] = pyglet.graphics.Batch()
        self.batches['hazard'] = pyglet.graphics.Batch()
        self.batches['guiback'] = pyglet.graphics.Batch()
        self.batches['guimid'] = pyglet.graphics.Batch()
        self.batches['gui'] = pyglet.graphics.Batch()
        self.batches['tutorial'] = pyglet.graphics.Batch()
        self.batches['tutorialtext'] = pyglet.graphics.Batch()
        self.batches['guitop'] = pyglet.graphics.Batch()
        self.batches['guitoptext'] = pyglet.graphics.Batch()

        pyglet.clock.schedule(self.update)
        pyglet.app.run()