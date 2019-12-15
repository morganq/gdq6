if __name__ == "__main__":
    import pyglet
    window = pyglet.window.Window(960, 720)
    import game
    g = game.Game(window)
    g.run()