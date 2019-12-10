import pyglet
import mapgen

def create_scene(game):
    scene = []

    game.batches['map'] = pyglet.graphics.Batch()

    mg = mapgen.MapGenerator(game, game.batches['map'], 800, 600, x = 80, y = 20)
    scene.append(mg)

    return scene