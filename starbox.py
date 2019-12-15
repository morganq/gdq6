import pyglet
import math

class StarBox(pyglet.sprite.Sprite):
    def __init__(self, game, x, y, stars):
        self.game = game
        self.num_stars = stars
        image_box = pyglet.image.load("resources/starbox.png")
        image_box.anchor_x = image_box.width
        self.image_star = pyglet.image.load("resources/star.tif")
        self.game.sound.play("swipe")
    
        super().__init__(image_box,
            x=x+game.level.mapgen.x,
            y=y+game.level.mapgen.y,
            batch=game.batches['guiback'],
            subpixel=True)
        
        self.star_t = 0
        self.time = 0
        self.child_stars = []

    def update(self, delta_time):
        self.time += delta_time
        if self.time <= 5:
            if len(self.child_stars) < 5:
                si = len(self.child_stars)
                self.star_t += delta_time * 2.5
                if self.star_t >= 1:
                    new_star = pyglet.sprite.Sprite(
                        self.image_star,
                        x=self.x - self.width + 9 + si*17,
                        y=self.y + 17,
                        subpixel=True,
                        batch=self.game.batches['guimid'])
                    new_star.t = 0
                    if si < self.num_stars:
                        new_star.color = (255,255,0)
                        self.game.sound.play('star')
                    else:
                        new_star.color = (160,160,160)
                    self.child_stars.append(new_star)
                    self.star_t = 0
            for star in self.child_stars:
                if star.t < 1:
                    star.t = min(star.t + delta_time * 8, 1)
                    star.scale = math.sin(star.t * 2) * 1.12
        if self.time > 5:
            if self.child_stars:
                self.game.level.stars.extend(self.child_stars[0:self.num_stars])
                for star in self.child_stars[self.num_stars:]:
                    star.visible = False
                    star.delete()
                self.child_stars = []
            self.scale = max(6 - self.time, 0)
        if self.time >= 6:
            self.game.scene.remove(self)
            self.delete()