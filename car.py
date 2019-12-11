import pyglet
from gameobj import GameObject
import random
import math

MAX_SPEED = {
    'basic':6.0,
    'main':8.0,
    'highway':12.0
}
ACCEL = 3

class Car(pyglet.sprite.Sprite):
    radius = 14
    def __init__(self, game, node):
        self.game = game
        self.last_node = node
        self.current_edge = random.choice(list(node.edges))
        self.directions = []
        graphic = pyglet.image.load("resources/car32.png")
        graphic.anchor_x = graphic.width//2
        graphic.anchor_y = graphic.height//2
        super().__init__(
            graphic,
            x=0,
            y=0,
            batch=game.batches['foreground'],
            subpixel=True
            )
        self.color=(0,0,0)
        self.scale = 0.8
        self.set_position_angle(node.pt, 1.2)
        self.map_pos = node.pt
        self.node_t = 0

        self.speed = 0
        self._state = "cruising"
        self.time = 0

    def set_position_angle(self, pos, angle):
        self.x = pos.x + self.game.level.mapgen.x
        self.y = pos.y + self.game.level.mapgen.y
        self.rotation = angle * 180 / 3.14159

    def update(self, delta_time):
        self.time += delta_time
        if self.directions:
            self.color = (0,0,0)
        else:
            c = -math.cos(self.time * 8) * 30 + 30
            self.color = (0,c,c)
        if self._state == "cruising":
            self.speed += ACCEL * delta_time
            maxspeed = MAX_SPEED[self.current_edge.road.kind]
            if self.speed > maxspeed:
                self.speed = maxspeed
            
            if self.last_node == self.current_edge.node1:
                next_node = self.current_edge.node2
            elif self.last_node == self.current_edge.node2:
                next_node = self.current_edge.node1
            else:
                print("CAR HAS FALLEN OFF TRACK!!")
            delta = next_node.pt - self.last_node.pt
            dist = delta.get_length()
            dt = self.speed / dist * delta_time
            if self.node_t + dt >= 1:
                self.node_t = 0
                if self.directions:
                    if self.directions[0] in next_node.edges:
                        self.current_edge = self.directions.pop(0)
                else:
                    next_edge_choices = list(next_node.edges)
                    if len(next_edge_choices) > 1:
                        next_edge_choices.remove(self.current_edge)
                    self.current_edge = random.choice(next_edge_choices)
                self.last_node = next_node
            else:
                self.node_t += dt
            self.map_pos = self.last_node.pt + delta * self.node_t
            angle, _ = delta.get_circular()
            self.set_position_angle(self.map_pos, angle + 3.14159 / 2)
