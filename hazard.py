import pyglet
import mapgen as mapgenmodule
import polygon
from vector import Vector
import math

HAZARD_COLOR = (221,97,42,255)

class HazardCreator(pyglet.sprite.Sprite):
    def __init__(self, game, icon, spawn, x, y, seconds, batch):
        self.game = game
        self.spawn = spawn
        self.time_left = seconds
        self.time = 0
        super().__init__(
            icon,
            x=x + game.level.mapgen.x,
            y=y + game.level.mapgen.y,
            batch=batch,
            subpixel=True
        )
        self.timer = pyglet.text.Label(
            str(int(seconds)), font_name="Menlo", font_size=16, anchor_x="center", anchor_y="center",
            bold=True,
            color=HAZARD_COLOR,
            batch=self.game.batches['hazard'],
            x = x + game.level.mapgen.x - 25,
            y = y + game.level.mapgen.y + 20
        )        
        self.map_pos = Vector(x,y)
        self.timer.visible = False
        self.color = HAZARD_COLOR[0:3]
        self.opacity = 0

    def update(self, delta_time):
        
        self.time += delta_time
        self.opacity = min(self.time, 1) * 255
        self.timer.opacity = min(self.time, 1) * 255
        self.time_left -= delta_time
        self.timer.text = str(int(self.time_left))
        if self.time > 1:
            self.timer.visible = True
            if self.time_left > 3:
                self.opacity = (self.time_left % 1) * 127 + 127
            else:
                self.opacity = (self.time_left % 0.5) * 255 + 127
            if self.time_left <= 0:
                s = self.spawn(self.game, self.x, self.y)
                self.game.scene.append(s)
                self.game.scene.remove(self)
                self.timer.delete()
                self.delete()
                return


class Hazard:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.radius = 0
        self.cars_in_range = []
        self.game.level.mapgen.shake()

    def update(self, delta_time):
        for car in self.game.level.cars:
            dist = (Vector(car.x, car.y) - Vector(self.x, self.y)).get_sq_length()
            if dist < self.radius ** 2:
                if car in self.cars_in_range:
                    self.on_car_stay(car)
                else:
                    self.on_car_enter(car)
                    self.cars_in_range.append(car)
            else:
                if car in self.cars_in_range:
                    self.cars_in_range.remove(car)

    def on_car_enter(self, car):
        pass

    def on_car_stay(self, car):
        pass

class CircleHazard(Hazard):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.circle = polygon.Polygon(
            x,
            y,
            self.get_diagonal_points(), (*HAZARD_COLOR[:3], 150), 4, self.game.batches['hazard'])
        self.border = polygon.Circle(
            x,y,self.radius + 1, HAZARD_COLOR, 3, self.game.batches['hazard']
        )        

    def get_diagonal_points(self):
        points = []
        step = 7
        y = -math.ceil(self.radius / step) * step
        while y <= self.radius:
            if y < -self.radius:
                y += step
                continue
            x1 = -math.sqrt(self.radius ** 2 - y ** 2)
            y1 = y
            x2 = -x1
            y2 = y
            y += step
            v1 = Vector(x1,y1)
            theta,rad = v1.get_circular()
            theta += 3.14159 / 4
            rv1 = Vector.from_circular(theta, rad)
            v2 = Vector(x2,y2)
            theta,rad = v2.get_circular()
            theta += 3.14159 / 4
            rv2 = Vector.from_circular(theta, rad)
            points.extend([rv1, rv2])
        
        if len(points) < 2:
            points = [Vector(0,0), Vector(0,0)]
        return points        

class NukeHazard(CircleHazard):
    def __init__(self, game, x, y, hazard_power):
        self.radius = 1
        self.hazard_power = hazard_power
        super().__init__(game, x, y)
        self.damage_tick = 0
        self.initial_target_radius = 24 + self.hazard_power * 10
        self.time = 0
        self.game.sound.play("nuke")

    def update(self, delta_time):
        super().update(delta_time)
        self.damage_tick -= delta_time
        self.time += delta_time
        z = int(math.sin(self.time * 10) * 20) + 100
        #self.circle.color = (255, 0, 0, z)
        if self.radius < self.initial_target_radius and self.time < 1:
            self.radius = min(self.radius + 180 * delta_time, self.initial_target_radius)
        if self.time > 3.0 and self.time < 10.0:
            self.radius += delta_time * (4 + self.hazard_power * 3)
        if self.time > 30.0:
            self.radius -= delta_time * 20
            self.border.radius = self.radius + 1        
            if self.radius <= 1:
                self.circle.delete()
                self.border.delete()
                self.game.scene.remove(self)
                return
        self.border.radius = self.radius + 1
        self.circle.set_points(self.get_diagonal_points())
        
    def on_car_stay(self, car):
        if car.is_president:
            if self.damage_tick <= 0:
                self.damage_tick = 2
                self.game.level.take_damage(1)


    def on_car_enter(self, car):
        if car.is_president and self.damage_tick <= 0:
            self.game.level.take_damage(5)
            self.damage_tick = 2
        else:
            car.die()


class MeteorHazard(CircleHazard):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.radius = 60
        self.time = 0
        self.damage_tick = 0
        self.game.sound.play("meteor")

    def update(self, delta_time):
        super().update(delta_time)
        self.time += delta_time
        self.damage_tick -= delta_time
        self.radius -= delta_time * 2
        self.border.radius = self.radius + 1
        self.circle.set_points(self.get_diagonal_points())
        if self.radius <= 1:
            self.circle.delete()
            self.border.delete()
            self.game.scene.remove(self)
            return

    def on_car_enter(self, car):
        if car.is_president and self.damage_tick <= 0:
            self.game.level.take_damage(5)
            self.damage_tick = 2
        else:
            car.die()            

SPREADTIME = 10
class RiotHazard(CircleHazard):
    def __init__(self, game, node, spread=1, sound=True):
        super().__init__(game, node.pt.x + game.level.mapgen.x, node.pt.y + game.level.mapgen.y)
        self.radius = 8 + spread * 3
        self.node = node
        self.node.blockers.append(self)
        self.border.radius = self.radius + 1
        self.circle.set_points(self.get_diagonal_points())
        self.lines = []
                    
        for edge in node.edges:
            d = (edge.other_node(node).pt - node.pt).get_normalized()
            p = polygon.Polygon(self.x, self.y, 
            [d * self.radius, d * self.radius],
            HAZARD_COLOR, 5, self.game.batches['hazard']
            )
            self.lines.append(p)
        self.time = 0
        self.damage_tick = 0
        self.spread = spread
        self.has_spread = False
        if sound:
            self.game.sound.play("riot")

    def update(self, delta_time):
        super().update(delta_time)
        self.time += delta_time

        for car in self.game.level.cars:
            for i,direction in enumerate(car.directions):
                if direction.node1.blockers or direction.node2.blockers:
                    car.directions = car.directions[:max(i-1,0)]
                    break

        if self.spread > 0:
            for i,line in enumerate(self.lines):
                edge = list(self.node.edges)[i]
                other = edge.other_node(self.node)
                if other.blockers:
                    continue
                d = (other.pt - self.node.pt)
                dr = d.get_normalized()
                dist = d.get_length()
                nextrad = self.radius - 4
                line.set_points(
                    [
                        dr * self.radius,
                        dr * (self.radius + (dist - self.radius - nextrad) * min(self.time / SPREADTIME,1))
                    ]
                )
            if self.time >= SPREADTIME and not self.has_spread:
                self.has_spread = True
                for edge in self.node.edges:
                    other = edge.other_node(self.node)
                    if not other.blockers:
                        r = RiotHazard(self.game, other, self.spread - 1, sound=False)
                        self.game.scene.append(r)
                self.game.sound.play("riot")

        if self.time > 10 * (self.spread + 1):
            self.radius = max(self.radius - delta_time * 10, 1)
            self.border.radius = self.radius + 1
            self.circle.set_points(self.get_diagonal_points())            
            if self.radius <= 1:
                self.node.blockers.remove(self)
                self.circle.delete()
                self.border.delete()
                for line in self.lines:
                    line.delete()
                self.game.scene.remove(self)