import pyglet

class Sound:
    def __init__(self, game):
        self.game = game
        self.sounds = {
            'click':'resources/gridsnap.ogg',
            'place':'resources/place.ogg',
            'star':'resources/starding.ogg',
            'swipe':'resources/swipe.ogg',
            'warning':'resources/warning.ogg',
            'nuke':'resources/nuke.ogg',
            'meteor':'resources/meteor.ogg',
            'riot':'resources/riot.ogg',
            'die':'resources/die.ogg',
        }
        self._sounds = {}
        for name,resource in self.sounds.items():
            self._sounds[name] = {
                'object':pyglet.media.StaticSource(pyglet.media.load(resource)),
                'last_time':-1,
                'player':pyglet.media.Player()
            }
        self.music = pyglet.media.load('resources/Uncan_-_01_-_Effemeah_Weeps.ogg')

    def play(self, name):
        #print(name)
        #self.player.queue(self.sounds[name])
        #self.player.play()
        s = self._sounds[name]
        if self.game.time > s['last_time'] + 0.05:
            s['player'] = s['object'].play()
            s['last_time'] = self.game.time