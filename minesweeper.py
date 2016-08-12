import sge


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
GRID_WIDTH = 20
GRID_LENGTH = 20
TILE_SIDE_DIM = 3 * WINDOW_WIDTH // (4 * GRID_WIDTH)

class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    pass


class Tile(sge.dsp.Object):

    def __init__(self, x, y):
        super().__init__(x, y, sprite=tile_sprite)


Game(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, window_text='Minesweeper by Dan Tinsley',
    collision_events_enabled=False)

tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=TILE_SIDE_DIM // 2,
    origin_y=TILE_SIDE_DIM // 2)
tile_sprite.draw_rectangle(0, 0, tile_sprite.width, tile_sprite.height, outline=sge.gfx.Color("black"))

background = sge.gfx.Background([], sge.gfx.Color("white"))

tile = Tile(1, 1)
objects = [tile]

sge.game.start_room = sge.dsp.Room(objects, background=background)

sge.game.start()
