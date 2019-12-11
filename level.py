import pyglet
import mapgen
import random
from car import Car

class Level:
    def __init__(self, game, num):
        self.num = num
        self.scene = None
        self.mapgen = None
        self.new_car_timer = 0.5
        self.game = game
        self.cars = []

    def create(self):
        self.scene = []

        self.mapgen = mapgen.Map(self.game, self.game.batches['map'], 800, 600, x = 80, y = 20)
        self.game.playercontrol.set_mapgen(self.mapgen)
        self.scene.append(self.mapgen)

        return self.scene

    def spawn_car(self):
        node = random.choice(list(self.mapgen.nodes))
        c = Car(self.game, node)
        self.scene.append(c)
        self.cars.append(c)

    def update(self, delta_time):
        self.new_car_timer -= delta_time
        if self.new_car_timer <= 0:
            self.new_car_timer += 10
            self.spawn_car()