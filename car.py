import pyglet
from gameobj import GameObject
import random
import math
from maphelp import *
from starbox import StarBox

HEURISTIC_SPEED = {
    'good':7.0,
    'okay':3.5,
    'bad':1.5
}

#MAX_SPEED = {
#    'basic':9.0,
#    'main':14.0,
#    'highway':20.0
#}
#MIN_SPEED = 2.0
#ACCEL = 5
#BRAKE = -8

MAX_SPEED = {
    'basic':10.0,
    'main':18.0,
    'highway':25.0
}
MIN_SPEED = 3.0
ACCEL = 8
BRAKE = -12

ROYAL_COLOR = (186,76,136)
NORMAL_COLOR = (40,40,40)

class Car(pyglet.sprite.Sprite):
    radius = 14
    car_image = "resources/car32.png"
    def __init__(self, game, node, target_nodes):
        self.game = game
        self.last_node = node
        self.current_edge = random.choice(list(node.edges))
        self.target_nodes = target_nodes
        self.directions = []
        self.given_directions = False
        self.is_president = False

        crows_dist = (target_nodes[0].pt - node.pt).get_length()
        self.good_time = crows_dist / HEURISTIC_SPEED['good']
        self.okay_time = crows_dist / HEURISTIC_SPEED['okay']
        self.bad_star_time = crows_dist / HEURISTIC_SPEED['bad']

        graphic = pyglet.image.load(self.car_image)
        graphic.anchor_x = graphic.width//2
        graphic.anchor_y = graphic.height//2
        super().__init__(
            graphic,
            x=0,
            y=0,
            batch=game.batches['foreground'],
            subpixel=True
            )
        self.color=NORMAL_COLOR
        self.base_color = NORMAL_COLOR
        self.scale = 0.8
        
        self.map_pos = node.pt
        self.node_t = 0

        self.speed = 0
        self._state = "cruising"
        self.time = 0
        self._interp_angle = 0
        self.set_position_angle(node.pt, 1.2, 10)
        self.die_timer = 0
        self.hover = False

    def set_position_angle(self, pos, angle, delta_time):
        self.x = pos.x + self.game.level.mapgen.x
        self.y = pos.y + self.game.level.mapgen.y
        
        dv1 = Vector.from_circular(self._interp_angle, 1)
        dv2 = Vector.from_circular(angle, 1)
        delta_angle = math.atan2(cross(dv1, dv2), dot(dv1, dv2))
        radjust = 2 * delta_time
        if delta_angle < -radjust:
            self._interp_angle += radjust
        elif delta_angle > radjust:
            self._interp_angle -= radjust
        else:
            self._interp_angle = angle


        self.rotation = self._interp_angle * 180 / 3.14159

    def add_random_direction(self):
        nn = None
        if self.current_edge.node1 == self.last_node:
            nn = self.current_edge.node2
        else:
            nn = self.current_edge.node1
        edges = list(nn.edges)
        if len(edges) > 1:
            edges.remove(self.current_edge)
        
        self.directions.append(random.choice(edges))

    def get_turns(self):
        distance = 0
        turns = []
        ln = self.last_node
        ce = self.current_edge        
        for edge in self.directions:
            dv1 = None
            nn = None
            if ce.node1 == ln:
                dv1 = ce.node2.pt - ce.node1.pt
                nn = ce.node2
            else:
                dv1 = ce.node1.pt - ce.node2.pt
                nn = ce.node1
            distance += dv1.get_length()
            dv1 = dv1.get_normalized()    

            dv2 = None
            if edge.node1 == nn:
                dv2 = edge.node2.pt - nn.pt
            else:
                dv2 = edge.node1.pt - nn.pt
            dv2 = dv2.get_normalized()
            delta_angle = math.atan2(cross(dv1, dv2), dot(dv1, dv2))
            if delta_angle > 0.2:
                turns.append(("left", nn, edge.road.name))
            elif delta_angle < -0.2:
                turns.append(("right", nn, edge.road.name))
            else:
                turns.append((None, nn, edge.road.name))
            
            ln = nn
            ce = edge        
        return turns

    def complete_trip(self):
        self.game.level.cars.remove(self)
        self.game.scene.remove(self)
        if self.game.playercontrol.selected_car == self:
            self.game.playercontrol.say("You have arrived at your destination", time_adjust=6.0)
            self.game.playercontrol.deselect()

        if self.time > self.bad_star_time:
            num_stars = 1
        elif self.time > self.okay_time:
            num_stars = 2
        elif self.time > self.good_time:
            num_stars = 3
        else:
            num_stars = random.randint(4,5)
        self.game.scene.append(StarBox(self.game, self.map_pos.x, self.map_pos.y, num_stars))
        self.delete()

    def die(self):
        if self._state != "dying":
            self.game.sound.play("die")
        self._state = "dying"

    def update(self, delta_time):
        self.time += delta_time
        if self.given_directions:
            self.color = self.base_color
        else:
            c = -math.cos(self.time * 8) * 30 + 30
            self.color = (
                self.base_color[0],
                min(self.base_color[1] + c, 255),
                min(self.base_color[2] + c/2, 255))

        if self._state == "dying":
            self.rotation += delta_time * 720
            self.scale -= delta_time
            if self.scale <= 0:
                self.game.level.cars.remove(self)
                self.game.scene.remove(self)
                if self.game.playercontrol.selected_car == self:
                    self.game.playercontrol.say("You have arrived at your destination", time_adjust=6.0)
                    self.game.playercontrol.deselect()                
                self.game.scene.append(StarBox(self.game, self.map_pos.x, self.map_pos.y, 0))
                self.delete()
                return

        if self._state == "done":
            self.speed = 0
            self.scale -= delta_time
            if self.scale <= 0:
                self.complete_trip()
                return

        if self._state == "cruising":
            if self.hover:
                self.scale = min(self.scale + delta_time * 4, 0.95)
            else:
                self.scale = max(self.scale - delta_time * 4, 0.8)            
            if not self.directions:
                self.add_random_direction()

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

            # If we're about to cross to the next node
            if self.node_t + dt >= 1:
                if next_node in self.target_nodes:
                    self.target_nodes.remove(next_node)
                    if len(self.target_nodes) == 0:
                        self._state = "done"
                self.node_t = 0
                if self.directions:
                    if self.directions[0] in next_node.edges:
                        self.current_edge = self.directions.pop(0)
                self.last_node = next_node
            else: # If we're not about to cross to the next node
                self.node_t += dt
                if self.directions:
                    turns = self.get_turns()
                    needs_stop = False
                    if self.current_edge.road.kind == "basic":
                        needs_stop = True
                    elif self.current_edge.road.kind == "main":
                        needs_stop = False
                    elif self.current_edge.road.kind == "highway":
                        needs_stop = False                        
                    if needs_stop or turns[0][0] != None:
                        turn_pt = turns[0][1].pt
                        dist = (turn_pt - self.map_pos).get_length()
                        seconds = dist / self.speed
                        if self.speed + BRAKE * seconds > 0:
                            self.speed = max(self.speed + (-ACCEL + BRAKE) * delta_time, MIN_SPEED)
            self.map_pos = self.last_node.pt + delta * self.node_t
            angle, _ = delta.get_circular()
            self.set_position_angle(self.map_pos, angle + 3.14159 / 2, delta_time)


class Limo(Car):
    car_image = "resources/limo32.png"
    radius = 42
    def __init__(self, game, node, target_nodes):
        super().__init__(game, node, target_nodes)
        self.color = ROYAL_COLOR
        self.base_color = ROYAL_COLOR
        self.is_president = True