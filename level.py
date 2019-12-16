import pyglet
import mapgen
import random
from car import Car, Limo, ROYAL_COLOR
from starbox import StarBox
from vector import Vector
from polygon import Polygon
import hazard
from presidentnotice import PresidentNotice
import sys
import tutorial

VICTORY_COLOR = (0,125,68)
MAPXOFF = 16

class Level:
    def __init__(self, game, num):
        self.num = num
        self.scene = None
        self.mapgen = None
        self.new_car_timer = 1.5
        self.new_hazard_timer = 30
        self.game = game
        self.cars = []
        self.hazard_images = {}
        for hz in ['nuke','meteor', 'molotov']:
            img = pyglet.image.load("resources/%s.png" % hz)
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2
            self.hazard_images[hz] = img
        self.stars = []
        self.game_over = False
        self.president = None
        self.notice = None
        self.lose = False
        self.time = 0
        self.end_time = 0
        self.star_background_x = 0
        self.star_background1 = None
        self.star_background2 = None
        self.star_mid_x = 642
        self.changed_to_health = False
        self.image_health = pyglet.image.load("resources/health.png")
        self.hazard_power = 1

        self.tut3_time = None
        self.tut4_time = None

        self.vip_text = pyglet.text.Label(
            "",
            font_size=8,
            bold=True,
            x=736, y=29,
            color=(255,255,255,255), batch=game.batches['gui'])
        self.president_health_text = pyglet.text.Label(
            "", 
            font_size=10,
            x=480, y = 5,
            bold=True,
            anchor_x="center",
            color=(*ROYAL_COLOR,255), batch=game.batches['gui'])

    def create(self):
        self.scene = []

        self.mapgen = mapgen.Map(self.game, self.game.batches['map'], 800, 600, x = 80, y = 60)
        self.game.playercontrol.set_mapgen(self.mapgen)
        self.scene.append(self.mapgen)

        self.tut = tutorial.Tutorial(self.game)
        self.scene.append(self.tut)

        self.star_background1 = Polygon(
            73, 18,
            [
                Vector(0,0), Vector(0,0),
                Vector(0,29), Vector(0,29)
            ],
            (*mapgen.BORDER_COLOR[:3], 255),1,self.game.batches['guiback'], pyglet.gl.GL_POLYGON
        )
        self.star_background2 = Polygon(
            73, 18,
            [
                Vector(0,0), Vector(0,0),
                Vector(0,29), Vector(0,29)
            ],
            (*ROYAL_COLOR, 255),1,self.game.batches['guiback'], pyglet.gl.GL_POLYGON
        )        

        # DEBUG
        for i in range(0):
            s = pyglet.sprite.Sprite(pyglet.image.load("resources/star.png"), batch=self.game.batches['gui'])
            self.stars.append(s)

        return self.scene

    def spawn_car(self, limo=False):
        node1 = random.choice(list(self.mapgen.non_border_nodes))
        node2 = random.choice(list(self.mapgen.non_border_nodes))
        if limo:
            c = Limo(self.game, node1, random.choices(list(self.mapgen.non_border_nodes), k=5))
            self.president = c
            self.notice = PresidentNotice(self.game, "The President Needs Directions...!", ROYAL_COLOR)
            self.scene.append(self.notice)
        else:
            c = Car(self.game, node1, [node2])
            
        self.scene.append(c)
        self.cars.append(c)

        #self.scene.append(StarBox(self.game, 50, 50, 4))

    def spawn_hazard(self):
        hazard_type = random.choice([
            'nuke',
            'meteor strike',
            'riot'
            ])
        if hazard_type == "nuke":
            x = random.randint(25, self.mapgen.width-25)
            y = random.randint(25, self.mapgen.height-25)
            h = hazard.HazardCreator(
                self.game,
                self.hazard_images['nuke'],
                lambda game,x,y:hazard.NukeHazard(game, x, y, self.hazard_power),
                x, y, 10, self.game.batches['hazard'])
            self.game.scene.append(h)
        elif hazard_type == "meteor strike":
            x = random.randint(100, self.mapgen.width-100)
            y = random.randint(100, self.mapgen.height-100)
            for i in range(2 + self.hazard_power):
                near_vect = Vector.from_circular(
                    i * 6.2818 / (2 + self.hazard_power),
                    random.randint(20 + self.hazard_power * 20, 50 + self.hazard_power * 20)) + Vector(x,y)
                h = hazard.HazardCreator(
                    self.game,
                    self.hazard_images['meteor'],
                    hazard.MeteorHazard,
                    near_vect.x, near_vect.y, 6 - i * 0.33, self.game.batches['hazard'])
                self.game.scene.append(h)
        if hazard_type == "riot":
            node = random.choice(self.mapgen.non_border_nodes)
            h = hazard.HazardCreator(
                self.game,
                self.hazard_images['molotov'],
                lambda game,x,y:hazard.RiotHazard(game, node, spread=self.hazard_power),
                node.pt.x, node.pt.y, 10, self.game.batches['hazard'])
            self.game.scene.append(h)                
        self.game.sound.play("warning")
        self.tut.show("hazards")
        if self.tut4_time is None:
            self.tut4_time = 10.0

    def take_damage(self, amount):
        if amount > 0:
            self.mapgen.shake()
            if amount > len(self.stars):
                self.lose = True
                self.president.die()
                amount = len(self.stars)
            destroy = self.stars[len(self.stars) - amount:]
            for star in destroy:
                star.delete()
            self.stars = self.stars[0:len(self.stars) - amount]


    def update(self, delta_time):
        self.new_car_timer -= delta_time
        self.new_hazard_timer -= delta_time
        self.time += delta_time

        if self.time > 3.0:
            self.tut.show("intro")
            if self.game.playercontrol.selected_car:
                self.tut.show("draw")
                good_directions = False
                for edge in self.game.playercontrol.selected_car.directions:
                    if self.game.playercontrol.selected_car.target_nodes:
                        if edge.node1 == self.game.playercontrol.selected_car.target_nodes[0]:
                            good_directions = True
                        if edge.node2 == self.game.playercontrol.selected_car.target_nodes[0]:
                            good_directions = True                        
                if (self.game.playercontrol.selected_car.given_directions
                    and good_directions
                    and not self.game.playercontrol.drawing):
                    self.tut.hide("draw")
                    if self.tut3_time is None:
                        self.tut3_time = 3.0

            if self.tut3_time is not None:
                self.tut3_time -= delta_time
                if self.tut3_time <= 0:
                    self.tut.show("stars")
                if self.tut3_time < -16:
                    self.tut.hide("stars")
            if self.cars and self.cars[0]._state == "done":
                self.tut.hide("stars")
            if self.tut4_time is not None:
                self.tut4_time -= delta_time
                if self.tut4_time < 0:
                    self.tut.hide("hazards")

        if self.time > 180:
            self.hazard_power = 2
        if self.president:
            self.hazard_power = 3

        if len(self.stars) == 0:
            self.new_hazard_timer = 3.0

        if self.game_over and self.time > self.end_time:
            sys.exit()

        if self.president and not self.game_over:
            if len(self.president.target_nodes) == 0:
                self.end_time = self.time + 8
                self.game_over = True
                minutes = int(self.time / 60)
                seconds = int(self.time % 60)
                self.notice = PresidentNotice(self.game, "YOU WIN! Your Time: %d:%2d" % (minutes, seconds), VICTORY_COLOR)
                self.game.scene.append(self.notice)
            if self.lose:
                self.game_over = True
                self.notice = PresidentNotice(self.game, "YOU LOSE...", hazard.HAZARD_COLOR[:3])
                self.game.scene.append(self.notice)
                self.end_time = self.time + 8


        if not self.game_over:
            min_cars = 1
            max_cars = 999
            if self.time < 40:
                min_cars = 1
                max_cars = 1
            elif self.time < 80:
                min_cars = 2
                max_cars = 2
            else:
                min_cars = 3
            if (self.new_car_timer <= 0 or (len(self.cars) <= min_cars and self.time > 10.0)) and len(self.cars) < max_cars:
                if self.tut.showing_message not in ["intro", "draw"]:
                    if self.president:
                        self.new_car_timer = 25
                    if self.time < 5:
                        self.new_car_timer = 30
                    elif self.time < 90:
                        self.new_car_timer = 30
                    else:
                        self.new_car_timer = 20
                    self.spawn_car()
            if self.new_hazard_timer <= 0:
                self.spawn_hazard()
                if self.president:
                    self.new_hazard_timer = 8
                elif self.time < 90:
                    self.new_hazard_timer = 20 + random.randint(0,12)
                else:
                    self.new_hazard_timer = 9 + random.randint(0,12)

            if len(self.stars) > 40 and self.president == None:
                self.spawn_car(limo=True)
                self.new_car_timer = 20
                self.new_hazard_timer = 6

        if self.stars and not self.president:
            self.star_background_x = min(self.star_background_x + delta_time * 400, self.mapgen.width+MAPXOFF)
            self.star_background1.set_points([
                Vector(0,0), Vector(min(self.star_mid_x, self.star_background_x),0),
                Vector(min(self.star_mid_x, self.star_background_x),29), Vector(0,29)
            ])
            self.star_background2.set_points([
                Vector(min(self.star_background_x, self.star_mid_x + 2),0),
                Vector(min(self.star_background_x, self.mapgen.width + MAPXOFF),0),
                Vector(min(self.star_background_x, self.mapgen.width + MAPXOFF),29),
                Vector(min(self.star_background_x, self.star_mid_x + 2),29)
            ])
            if self.star_background_x >= self.mapgen.width+MAPXOFF:
                self.vip_text.text = "%d MORE STARS UNTIL VIP" % (40 - len(self.stars))

        if self.president:
            self.vip_text.text = ""
            self.president_health_text.text = "PRESIDENT'S HEALTH"
            if self.star_background_x > 0:
                self.star_background_x = max(self.star_background_x - delta_time * 500, 0)
                self.star_background1.set_points([
                    Vector(0,0), Vector(max(self.star_mid_x, self.star_background_x),0),
                    Vector(max(self.star_mid_x, self.star_background_x),29), Vector(0,29)
                ])
                self.star_background2.set_points([
                    Vector(min(self.star_background_x, self.star_mid_x + 2),0),
                    Vector(self.mapgen.width + MAPXOFF,0),
                    Vector(self.mapgen.width + MAPXOFF,29),
                    Vector(min(self.star_background_x, self.star_mid_x + 2),29)
                ])
            self.changed_to_health = True
            
        for i,star in enumerate(self.stars):
            if self.changed_to_health and star.image != self.image_health:
                star.image = self.image_health
                star.color = (255,255,255)
                star.scale = 1
            fivespans = int(i / 5) * 10
            vertical = int((i % 5) % 2) * 6
            target_pos = Vector(self.mapgen.x - 4 + i*14 + fivespans, 18 + vertical)
            star_pos = Vector(star.x, star.y)
            if (target_pos - star_pos).get_sq_length() < 1:
                star.x = target_pos.x
                star.y = target_pos.y
            else:
                delta = (target_pos - star_pos)
                star.x += delta.x / 10
                star.y += delta.y / 10