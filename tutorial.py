import polygon
import pyglet
import player
from vector import Vector
import random
import hazard

# Need to appear in the least obnoxious location
# Package fonts

TUTORIAL_STRINGS = {
    "intro":"This driver has no idea how to get where they're going! Click on the car to select it.",
    "draw":"Click and drag a path from the car to give the driver directions. They need to reach their destination marked with an X.",
    #"roads":"The highway is the fastest way to travel, and the major roads are pretty quick too.",
    "stars":"Find them a quick route and you'll earn stars from satisfied drivers. Highways and major roads have higher speed limits.",
    "hazards":"Try to avoid disasters and riots. Dead drivers give poor reviews."
}

WIDTH = 400
HEIGHT = 130

class Tutorial:
    def __init__(self, game):
        self.game = game
        self.messages = TUTORIAL_STRINGS
        self.arrow = polygon.Polygon(0,0,
            [Vector(0,0), Vector(0,0)],
            player.SELECTION_COLOR_1, 2, self.game.batches['tutorial'], pyglet.gl.GL_TRIANGLES
        )
        self.arrow.visible = False
        self.arrow_line = polygon.Polygon(0,0,
            [Vector(0,0), Vector(0,0)],
            player.SELECTION_COLOR_1, 2, self.game.batches['tutorial'], pyglet.gl.GL_LINES
        )       
        self.arrow_line.visible = False
        self.background = polygon.Polygon(0, 0,
            [Vector(0,0), Vector(WIDTH, 0), Vector(WIDTH,HEIGHT), Vector(0,HEIGHT)],
            player.SELECTION_COLOR_1, 1, self.game.batches['tutorial'], pyglet.gl.GL_POLYGON
        )
        self.background.visible = False

        self.text = pyglet.text.Label(
            "", font_name="Menlo", font_size=12, anchor_x="left", anchor_y="center",
            width=WIDTH - 40,
            height=HEIGHT - 30,
            multiline=True,
            color=(255,255,255,255),
            batch=self.game.batches['tutorialtext'],
            x = 10,
            y = 10
        )
        self.esc_text = pyglet.text.Label(
            "", font_name="Menlo", font_size=9, anchor_x="left", anchor_y="center",
            color=(255,255,255,255),
            batch=self.game.batches['tutorialtext'],
            x = 10,
            y = 10
        )
        #self.text.visible = False
        self.x = 0
        self.y = 0
        self.appear_time = 0
        self.showing_message = ""
        self.picked_spot = None
        self.show_t = 0

    def set_arrow(self, target):
        off = Vector(self.arrow.x, self.arrow.y)
        delta = target - off
        direction = delta.get_normalized()
        side = Vector(direction.y, -direction.x)
        W = 5
        AW = 16
        D1 = 40
        D2 = 20
        p_b1 = -side * W
        p_b2 = side * W
        p_f1 = delta - direction * D1 - side * W
        p_f2 = delta - direction * D1 + side * W
        p_a1 = delta - direction * D1 - side * AW
        p_a2 = delta - direction * D1 + side * AW
        p_a3 = delta - direction * D2
        self.arrow.set_points([
            p_b2, p_b1, p_f1,
            p_b2, p_f1, p_f2,
            p_a1, p_a2, p_a3
        ])
        self.arrow_line.set_points([
            p_b1, p_b2,
            p_b2, p_f2,
            p_f2, p_a2,
            p_a2, p_a3,
            p_a3, p_a1,
            p_a1, p_f1,
            p_f1, p_b1
        ])

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.background.x = x
        self.background.y =y
        self.arrow.x = x + WIDTH / 2
        self.arrow.y = y + HEIGHT / 2
        self.arrow_line.x = self.arrow.x
        self.arrow_line.y = self.arrow.y
        self.text.x = x + 20
        self.text.y = y + HEIGHT / 2
        self.esc_text.x = x + 120
        self.esc_text.y = y + 20

    def set_message_arrow(self, message_name):
        if message_name == "intro":
            c = self.game.level.cars
            if c:
                c = c[0]
                self.set_arrow(Vector(c.x, c.y))
            else:
                self.hide()
        elif message_name == "hazards":
            for obj in self.game.level.scene:
                if isinstance(obj, hazard.HazardCreator):
                    self.set_arrow(Vector(obj.x, obj.y))
        else:
            self.arrow.visible = False
            self.arrow_line.visible = False

    def hide(self, which=None):
        if which is not None:
            if self.showing_message != which:
                return
        self.showing_message = None
        self.text.visible = False
        self.text.text = ""
        self.esc_text.text = ""
        self.background.visible = False
        self.arrow.visible = False
        self.arrow_line.visible = False

    def find_spot(self):
        available = [0,1,2,3]
        spots = [
            Vector(20, 20),
            Vector(self.game.window.width - WIDTH - 20, 20),
            Vector(20, self.game.window.height - HEIGHT - 20),
            Vector(self.game.window.width - WIDTH - 20, self.game.window.height - HEIGHT - 20),
        ]
        objs = [c.map_pos for c in self.game.level.cars]
        if self.game.playercontrol.selected_car and self.game.playercontrol.selected_car.target_nodes:
            objs.append(self.game.playercontrol.selected_car.target_nodes[0].pt)
        for o in self.game.level.scene:
            if isinstance(o, hazard.HazardCreator):
                objs.append(o.map_pos)
        for pos in objs:
            if 0 in available and pos.x < 400 and pos.y < 300:
                available.remove(0)
            if 1 in available and pos.x >= 400 and pos.y < 300:
                available.remove(1)
            if 2 in available and pos.x < 400 and pos.y >= 300:
                available.remove(2)
            if 3 in available and pos.x >= 400 and pos.y >= 300:
                available.remove(3)
        if self.picked_spot is not None:
            if self.picked_spot in available:
                return spots[self.picked_spot]
        if available:
            self.picked_spot = random.choice(available)
        return spots[self.picked_spot]

    def show(self, message_name):
        if message_name in self.messages:
            self.show_t = 0
            self.text.visible = True
            self.text.text = self.messages[message_name]
            self.background.visible = True
            self.arrow.visible = True
            self.arrow_line.visible = True
            self.appear_time = 12.0
            self.showing_message = message_name
            self.set_message_arrow(message_name)
            self.esc_text.text = "[ESC] to skip tutorial"
            del self.messages[message_name]
            

    def update(self, delta_time):
        spot = self.find_spot()
        self.set_pos(spot.x, spot.y)            
        self.set_message_arrow(self.showing_message)
        self.appear_time -= delta_time
        if self.show_t < 1:
            self.show_t = min(self.show_t + delta_time * 8, 1)
            self.background.color = (
                int(0 * (1 - self.show_t) + player.SELECTION_COLOR_1[0] * self.show_t),
                int(0 * (1 - self.show_t) + player.SELECTION_COLOR_1[1] * self.show_t),
                int(0 * (1 - self.show_t) + player.SELECTION_COLOR_1[2] * self.show_t),
                255
            )
