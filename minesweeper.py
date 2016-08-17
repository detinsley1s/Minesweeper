import random
import sge

# For determining the dimensions of the board
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
GRID_WIDTH = 20
GRID_HEIGHT = 20
TILE_SIDE_DIM = WINDOW_HEIGHT // GRID_HEIGHT

# For keeping track of the status of each individual cell
UNCLICKED = 0
CLICKED = 1
FLAGGED = 2


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()
        elif key == 'n':
            start_new_game()

    def event_close(self):
        self.end()

    def event_mouse_button_release(self, button):

        global mines_left

        # x, y are switched because Cartesian coords are different from list coords    
        mouse_x_loc = int(sge.mouse.get_y() // TILE_SIDE_DIM)
        mouse_y_loc = int(sge.mouse.get_x() // TILE_SIDE_DIM)

        if not game_is_over and 0 <= mouse_y_loc < GRID_WIDTH and 0 <= mouse_x_loc < GRID_HEIGHT:
            
            # left button is for clicking the cell
            # right button is for flagging the cell
            if button == 'left' and board_cell_statuses[mouse_x_loc][mouse_y_loc] == UNCLICKED:
                if mine_board[mouse_x_loc][mouse_y_loc] == 'M':
                    game_over('l')
                elif mine_board[mouse_x_loc][mouse_y_loc] == 0:
                    display_adjacent_tiles(mouse_x_loc, mouse_y_loc)
                else:
                    board_cell_statuses[mouse_x_loc][mouse_y_loc] = CLICKED
                make_new_cell = True
            elif button == 'right':
                if board_cell_statuses[mouse_x_loc][mouse_y_loc] == UNCLICKED and mines_left > 0:
                    board_cell_statuses[mouse_x_loc][mouse_y_loc] = FLAGGED
                    mines_left -= 1
                elif board_cell_statuses[mouse_x_loc][mouse_y_loc] == FLAGGED:
                    board_cell_statuses[mouse_x_loc][mouse_y_loc] = UNCLICKED
                    mines_left += 1
                make_new_cell = True
            else:
                make_new_cell = False
            
            if make_new_cell:
                tiles[mouse_x_loc*GRID_HEIGHT + mouse_y_loc] = Tile(mouse_y_loc*TILE_SIDE_DIM,
                    mouse_x_loc*TILE_SIDE_DIM)

            # Checks for if player won
            if mines_left == 0 and not any(x == UNCLICKED for y in board_cell_statuses for x in y) and not game_is_over:
                game_over('w')


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
        if board_cell_statuses[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] == UNCLICKED:
            super().__init__(x, y, sprite=unclicked_tile_sprite)
        elif board_cell_statuses[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] == CLICKED:
            if mine_board[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] == 'M':
                super().__init__(x, y, sprite=mine_sprite)
            elif isinstance(mine_board[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM], int) and \
              mine_board[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM] > 0:
                flags_nearby = mine_board[y//TILE_SIDE_DIM][x//TILE_SIDE_DIM]
                super().__init__(x, y, sprite=number_tiles[flags_nearby-1])
            else:
                super().__init__(x, y, sprite=clicked_tile_sprite)
        else:
            super().__init__(x, y, sprite=flagged_tile_sprite)


def display_adjacent_tiles(x, y):
    """Displays all the tiles that are blank or that form a boundary
       when a blank cell is clicked on the board"""
    if mine_board[x][y] != 'M' and board_cell_statuses[x][y] == UNCLICKED:
        board_cell_statuses[x][y] = CLICKED
        tiles[x*GRID_HEIGHT + y] = Tile(y*TILE_SIDE_DIM, x*TILE_SIDE_DIM)
        if mine_board[x][y] == 0:
            if x - 1 >= 0:
                display_adjacent_tiles(x-1, y)
                if y - 1 >= 0 and mine_board[x-1][y-1] != 'M':
                       display_adjacent_tiles(x-1, y-1)
                if y + 1 <= GRID_WIDTH - 1 and mine_board[x-1][y+1] != 'M':
                       display_adjacent_tiles(x-1, y+1)
            if x + 1 <= GRID_HEIGHT - 1:
                display_adjacent_tiles(x+1, y)
                if y - 1 >= 0 and mine_board[x+1][y-1] != 'M':
                       display_adjacent_tiles(x+1, y-1)
                if y + 1 <= GRID_WIDTH - 1 and mine_board[x+1][y+1] != 'M':
                       display_adjacent_tiles(x+1, y+1)
            if y - 1 >= 0:
                display_adjacent_tiles(x, y-1)
            if y + 1 <= GRID_WIDTH - 1:
                display_adjacent_tiles(x, y+1)


def start_new_game():
    """Starts a new game and initializes the data"""
    global game_is_over, mines_left, tiles, mine_board, board_cell_statuses
   
    # Determines if the game ended 
    game_is_over = False
    
    # determines how many mines to have hidden
    mines_left = int(GRID_WIDTH * GRID_HEIGHT * 0.05)
    
    # Make every cell hidden and never clicked
    board_cell_statuses = initialize_cell_statuses()

    # generate the tiles for drawing at beginning of game
    tiles = generate_tiles()
    
    # Make initial hidden state of board
    mine_board = generate_hidden_cells()


def game_over(result):
    """Performs game over activities"""
    global game_is_over, mines_left

    game_is_over = True
    if result == 'l':
        reveal_board()
        mines_left = 0
        print('You lost. Press p to play again or q to quit')
    else:
        print('you won')


def reveal_board():
    """Reveals the entire board"""
    for row, r_val in enumerate(board_cell_statuses):
        for col, _ in enumerate(r_val):
            if board_cell_statuses[row][col] != CLICKED:
                board_cell_statuses[row][col] = CLICKED
                tiles[row*GRID_HEIGHT + col] = Tile(col*TILE_SIDE_DIM, row*TILE_SIDE_DIM)


def initialize_cell_statuses():
    statuses = []
    for _ in range(GRID_HEIGHT):
        statuses.append([UNCLICKED]*GRID_WIDTH)
    return statuses


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

description_font = sge.gfx.Font(size=36, underline=True)
mines_left_font = sge.gfx.Font(size=60)

# prepare the flag sprites
unclicked_tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
unclicked_tile_sprite.draw_rectangle(0, 0, unclicked_tile_sprite.width, unclicked_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("red"))
clicked_tile_sprite = sge.gfx.Sprite(width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
clicked_tile_sprite.draw_rectangle(0, 0, clicked_tile_sprite.width, clicked_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("white"))
flagged_tile_sprite = sge.gfx.Sprite(name='flag', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
flagged_tile_sprite.draw_rectangle(0, 0, flagged_tile_sprite.width, flagged_tile_sprite.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color((100, 100, 100, 100)))
mine_sprite = sge.gfx.Sprite(name='explosion', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
mine_sprite.draw_rectangle(0, 0, mine_sprite.width, mine_sprite.height,
    outline=sge.gfx.Color("black"))
number_1_sprite = sge.gfx.Sprite(name='one', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_1_sprite.draw_rectangle(0, 0, number_1_sprite.width, number_1_sprite.height,
    outline=sge.gfx.Color("black"))
number_2_sprite = sge.gfx.Sprite(name='two', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_2_sprite.draw_rectangle(0, 0, number_2_sprite.width, number_2_sprite.height,
    outline=sge.gfx.Color("black"))
number_3_sprite = sge.gfx.Sprite(name='three', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_3_sprite.draw_rectangle(0, 0, number_3_sprite.width, number_3_sprite.height,
    outline=sge.gfx.Color("black"))
number_4_sprite = sge.gfx.Sprite(name='four', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_4_sprite.draw_rectangle(0, 0, number_4_sprite.width, number_4_sprite.height,
    outline=sge.gfx.Color("black"))
number_5_sprite = sge.gfx.Sprite(name='five', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_5_sprite.draw_rectangle(0, 0, number_5_sprite.width, number_5_sprite.height,
    outline=sge.gfx.Color("black"))
number_6_sprite = sge.gfx.Sprite(name='six', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_6_sprite.draw_rectangle(0, 0, number_6_sprite.width, number_6_sprite.height,
    outline=sge.gfx.Color("black"))
number_7_sprite = sge.gfx.Sprite(name='seven', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_7_sprite.draw_rectangle(0, 0, number_7_sprite.width, number_7_sprite.height,
    outline=sge.gfx.Color("black"))
number_8_sprite = sge.gfx.Sprite(name='eight', directory='images/', width=TILE_SIDE_DIM, height=TILE_SIDE_DIM, origin_x=0, origin_y=0)
number_8_sprite.draw_rectangle(0, 0, number_8_sprite.width, number_8_sprite.height,
    outline=sge.gfx.Color("black"))

number_tiles = [number_1_sprite, number_2_sprite, number_3_sprite, number_4_sprite, number_5_sprite,
    number_6_sprite, number_7_sprite, number_8_sprite]


background = sge.gfx.Background([], sge.gfx.Color("white"))

sge.game.start_room = Room([], background=background)

sge.game.mouse.visible = True

start_new_game()

# code to look at hidden board in console
#for cell in mine_board:
#    print(''.join(map(str, cell)))

if __name__ == '__main__':
    sge.game.start()
