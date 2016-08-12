import sge


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
GRID_WIDTH = 20
GRID_HEIGHT = 20
TILE_SIDE_DIM = WINDOW_HEIGHT // GRID_HEIGHT

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


def generate_tiles():
    table = []
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            table.append(Tile(i*TILE_SIDE_DIM, j*TILE_SIDE_DIM))
    return table


Game(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, window_text='Minesweeper by Dan Tinsley',
    collision_events_enabled=False)

tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
tile_sprite.draw_rectangle(0, 0, tile_sprite.width, tile_sprite.height, outline=sge.gfx.Color("black"))

background = sge.gfx.Background([], sge.gfx.Color("white"))

tiles = generate_tiles()
objects = [*tiles]

sge.game.start_room = sge.dsp.Room(objects, background=background)

sge.game.start()
