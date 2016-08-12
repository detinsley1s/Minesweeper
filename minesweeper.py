import random
import sge


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
GRID_WIDTH = 20
GRID_HEIGHT = 20
TILE_SIDE_DIM = WINDOW_HEIGHT // GRID_HEIGHT

# determines how many mines to have hidden
mines_left = int(GRID_WIDTH * GRID_HEIGHT * 0.15)

# for keeping track of the status of each individual cell
cell_status = {'unclicked': 0, 'clicked': 1, 'flagged': 2}

# Make every cell hidden and never clicked
board_cell_statuses = []
for i in range(GRID_HEIGHT):
    board_cell_statuses.append([cell_status['unclicked']]*GRID_WIDTH)


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()

    def event_mouse_button_release(self, button):
        
        # x, y are switched because Cartesian coords are different from list coords    
        mouse_x_loc = int(sge.mouse.get_y() // TILE_SIDE_DIM)
        mouse_y_loc = int(sge.mouse.get_x() // TILE_SIDE_DIM)

        if 0 <= mouse_y_loc < GRID_WIDTH and 0 <= mouse_x_loc < GRID_HEIGHT:
            
            # left button is for clicking the cell
            # right button is for flagging the cell
            if button == 'left' and board_cell_statuses[mouse_x_loc][mouse_y_loc] != 1:
                board_cell_statuses[mouse_x_loc][mouse_y_loc] = 1
                make_new_cell = True
            elif button == 'right' and board_cell_statuses[mouse_x_loc][mouse_y_loc] == 0:
                board_cell_statuses[mouse_x_loc][mouse_y_loc] = 2
                make_new_cell = True
            else:
                make_new_cell = False
            
            if make_new_cell:
                tiles[mouse_x_loc*GRID_HEIGHT + mouse_y_loc] = Tile(mouse_y_loc*TILE_SIDE_DIM,
                    mouse_x_loc*TILE_SIDE_DIM)


class Room(sge.dsp.Room):

    def event_step(self, time_passed, delta_mult):

        # display the text
        sge.game.project_text(description_font, "Mines", WINDOW_WIDTH - 100, 150,
            color=sge.gfx.Color("black"), halign="center", valign="middle")
        sge.game.project_text(description_font, "Remaining", WINDOW_WIDTH - 100, 190,
            color=sge.gfx.Color("black"), halign="center", valign="middle")
        sge.game.project_text(mines_left_font, str(mines_left), WINDOW_WIDTH - 100, 250,
            color=sge.gfx.Color("black"), halign="center", valign="middle")

        # draw the tiles
        for tile in tiles:
            sge.game.project_sprite(tile.sprite, 0, tile.x, tile.y)


class Tile(sge.dsp.Object):

    def __init__(self, x, y):
        if board_cell_statuses[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] == cell_status['unclicked']:
            super().__init__(x, y, sprite=unclicked_tile_sprite)
        elif board_cell_statuses[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] == cell_status['clicked']:
            super().__init__(x, y, sprite=clicked_tile_sprite)
        else:
            super().__init__(x, y, sprite=flagged_tile_sprite)


def generate_tiles():
    """Draws the minesweeper grid"""
    table = []
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            table.append(Tile(j*TILE_SIDE_DIM, i*TILE_SIDE_DIM))
    return table


def generate_hidden_cells():
    """Makes the board, and places bombs, along with their hint numbers"""
    mine_board = []
    for i in range(GRID_HEIGHT):
        mine_board.append([0]*GRID_WIDTH)

    # Place the bombs in the grid
    total_mines_to_place = mines_left
    while total_mines_to_place > 0:
        rand_x = random.choice(range(GRID_HEIGHT))
        rand_y = random.choice(range(GRID_WIDTH))
        if mine_board[rand_x][rand_y] == 0:
            mine_board[rand_x][rand_y] = 'M'
            total_mines_to_place -= 1

    # Add the numbers to the grid
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if mine_board[i][j] == 'M':
               if i - 1 >= 0:
                   if j - 1 >= 0 and mine_board[i-1][j-1] != 'M':
                       mine_board[i-1][j-1] += 1
                   if j + 1 <= GRID_WIDTH - 1 and mine_board[i-1][j+1] != 'M':
                       mine_board[i-1][j+1] += 1
                   if mine_board[i-1][j] != 'M':
                       mine_board[i-1][j] += 1
               if i + 1 <= GRID_HEIGHT - 1:
                   if j - 1 >= 0 and mine_board[i+1][j-1] != 'M':
                       mine_board[i+1][j-1] += 1
                   if j + 1 <= GRID_WIDTH - 1 and mine_board[i+1][j+1] != 'M':
                       mine_board[i+1][j+1] += 1
                   if mine_board[i+1][j] != 'M':
                       mine_board[i+1][j] += 1
               if j - 1 >= 0 and mine_board[i][j-1] != 'M':
                   mine_board[i][j-1] += 1
               if j + 1 <= GRID_WIDTH - 1 and mine_board[i][j+1] != 'M':
                   mine_board[i][j+1] += 1
    return mine_board


Game(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, window_text='Minesweeper by Dan Tinsley', grab_input=True,
    collision_events_enabled=False)

# prepare the flag sprites
unclicked_tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
unclicked_tile_sprite.draw_rectangle(0, 0, unclicked_tile_sprite.width, unclicked_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("red"))
clicked_tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
clicked_tile_sprite.draw_rectangle(0, 0, clicked_tile_sprite.width, clicked_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("green"))
flagged_tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
flagged_tile_sprite.draw_rectangle(0, 0, flagged_tile_sprite.width, flagged_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("blue"))


background = sge.gfx.Background([], sge.gfx.Color("white"))

# generate the tiles for drawing at beginning of game
tiles = generate_tiles()

# Make initial hidden state of board
mine_board = generate_hidden_cells()

description_font = sge.gfx.Font(size=36, underline=True)
mines_left_font = sge.gfx.Font(size=60)

sge.game.start_room = Room([], background=background)

sge.game.mouse.visible = True

sge.game.start()
