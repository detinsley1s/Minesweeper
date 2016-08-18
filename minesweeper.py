#!/usr/bin/env python3

"""Minesweeper
Programmed by Daniel Tinsley
Copyright 2016

A simple Minesweeper clone developed
with the help of the SGE framework

Sound effects generated at www.bfxr.net
"""

import random
import sge


# For determining the dimensions of the board
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
GRID_WIDTH = 20
GRID_HEIGHT = 20
TILE_DIMS = WINDOW_HEIGHT // GRID_HEIGHT

# For keeping track of the status of each individual cell
UNCLICKED = 0
CLICKED = 1
FLAGGED = 2


class Game(sge.dsp.Game):
    """This class handles most parts of the game which work globally.

    Subclass of sge.dsp.Game

    Methods:
    event_close
    event_key_press
    event_mouse_button_release
    """

    def event_key_press(self, key, char):
        """Detect when a key is pressed on the keyboard.

        Overrides method from superclass sge.dsp.Game

        Parameters:
        key -- the identifier string of the key that was pressed
        char -- the Unicode character associated with the key press
        """
        if key == 'escape':
            self.event_close()
        elif key == 'n':
            start_new_game()

    def event_close(self):
        """Close the application."""
        self.end()

    def event_mouse_button_release(self, button):
        """Detect when a mouse button is released.

        Overrides method from superclass sge.dsp.Game

        Parameter:
        button -- the identifier string of the mouse button that was
                  released
        """
        # x, y are switched because grid coords are different from list coords
        mouse_x_loc = int(sge.mouse.get_y() // TILE_DIMS)
        mouse_y_loc = int(sge.mouse.get_x() // TILE_DIMS)

        if not board.board_is_complete and 0 <= mouse_y_loc < GRID_WIDTH and (
                0 <= mouse_x_loc < GRID_HEIGHT):

            # Left button is for clicking the cell
            # Right button is for flagging the cell
            if button == 'left':
                make_new_cell = board.cell_is_clicked(mouse_x_loc, mouse_y_loc)
            elif button == 'right':
                make_new_cell = board.cell_is_flagged(mouse_x_loc, mouse_y_loc)
            else:
                make_new_cell = False

            # Only make a new cell if it is necessary
            if make_new_cell:
                board.construct_cell(mouse_x_loc, mouse_y_loc)

            # Check if player won
            board.check_for_win()


class Room(sge.dsp.Room):
    """This class stores the settings and objects found in a level.

    Subclass of sge.dsp.Room

    Method:
    event_step
    """

    def event_step(self, time_passed, delta_mult):
        """Do level processing once each frame.

        Overrides method from superclass sge.dsp.Room

        Parameters:
        time_passed -- the total milliseconds that have passed during
                       the last frame
        delta_mult -- what speed and movement should be multiplied by
                      this frame due to delta timing
        """
        # Display the screen's text
        sge.game.project_text(
            DESCRIPTION_FONT, 'Mines', WINDOW_WIDTH - 100, 70,
            color=sge.gfx.Color('black'), halign='center', valign='middle'
        )
        sge.game.project_text(
            DESCRIPTION_FONT, 'Remaining', WINDOW_WIDTH - 100, 110,
            color=sge.gfx.Color('black'), halign='center', valign='middle'
        )
        sge.game.project_text(
            MINES_LEFT_FONT, str(board.mines_left), WINDOW_WIDTH - 100, 170,
            color=sge.gfx.Color('black'), halign='center', valign='middle'
        )
        sge.game.project_text(
            DESCRIPTION_FONT, 'Instructions', WINDOW_WIDTH - 100,
            WINDOW_HEIGHT - 168, color=sge.gfx.Color('black'), halign='center',
            valign='middle'
        )
        sge.game.project_text(
            INSTRUCTIONS_FONT, 'Left Mouse Button: Reveal Tile',
            WINDOW_WIDTH - 187, WINDOW_HEIGHT - 130,
            color=sge.gfx.Color('black'), halign='left', valign='middle'
        )
        sge.game.project_text(
            INSTRUCTIONS_FONT, 'Right Mouse Button: Flag Tile',
            WINDOW_WIDTH - 187, WINDOW_HEIGHT - 110,
            color=sge.gfx.Color('black'), halign='left', valign='middle'
        )
        sge.game.project_text(
            INSTRUCTIONS_FONT, 'N: New Game', WINDOW_WIDTH - 187,
            WINDOW_HEIGHT - 90, color=sge.gfx.Color('black'), halign='left',
            valign='middle'
        )
        sge.game.project_text(
            INSTRUCTIONS_FONT, 'Esc: Exit Game', WINDOW_WIDTH - 187,
            WINDOW_HEIGHT - 70, color=sge.gfx.Color('black'), halign='left',
            valign='middle'
        )

        # Displays game over text only when game is completed
        if board.board_is_complete:
            sge.game.project_text(
                GAME_OVER_FONT, board.result, WINDOW_WIDTH - 100, 290,
                color=sge.gfx.Color('red'), halign='center', valign='middle'
            )

        # Draw the tiles
        for tile in board.tiles:
            sge.game.project_sprite(tile.sprite, 0, tile.x, tile.y)


class Tile(sge.dsp.Object):
    """This class is responsible for the individual tiles.

    Subclass of sge.dsp.Object
    """

    def __init__(self, x, y, grid):
        """Determine the screen placement and sprite for the tile.

        Calls the superclass' constructor method to form the tile

        Parameters:
        x -- the x coordinate on a Cartesian plane of the tile
        y -- the y coordinate on a Cartesian plane of the tile
        grid -- the game's board where the tile will be located
        """
        row = y // TILE_DIMS
        col = x // TILE_DIMS
        if grid.cell_statuses[row][col] == UNCLICKED:
            super().__init__(x, y, sprite=UNCLICKED_TILE_SPRITE)
        elif grid.cell_statuses[row][col] == CLICKED:
            if grid.mine_board[row][col] == 'M':
                super().__init__(x, y, sprite=MINE_SPRITE)
            elif isinstance(grid.mine_board[row][col], int) and (
                    grid.mine_board[row][col] > 0):
                flags_nearby = grid.mine_board[row][col]
                super().__init__(x, y, sprite=NUMBER_TILES[flags_nearby-1])
            else:
                super().__init__(x, y, sprite=CLICKED_TILE_SPRITE)
        else:
            super().__init__(x, y, sprite=FLAGGED_TILE_SPRITE)


class Board:
    """This class is responsible for the game board and its functions.

    Methods:
    add_hint_numbers
    cell_is_clicked
    cell_is_flagged
    check_for_win
    construct_cell
    display_adjacent_tiles
    game_is_lost
    game_is_won
    generate_tiles
    initialize_cell_statuses
    initialize_hidden_board
    place_mines
    reveal_board

    Instance variables:
    board_is_complete -- boolean that denotes if the board is fully
                         exposed
    cell_statuses -- list of lists that denotes the cells which are
                     clicked, unclicked, or flagged
    mine_board -- list of lists that denotes what is located at each
                  cell (mines, hints, or blank tiles)
    mines_left -- integer that tracks the total mines remaining
    result -- string that stores the outcome of the game
    tiles -- list that contains the cell locations and sprites
    """

    def __init__(self):
        """Initialize the instance variables and prepare board."""
        self.mines_left = int(GRID_WIDTH * GRID_HEIGHT * 0.16)
        self.initialize_cell_statuses()
        self.initialize_hidden_board()
        self.place_mines()
        self.add_hint_numbers()
        self.generate_tiles()
        self.board_is_complete = False
        self.result = ''

    def display_adjacent_tiles(self, row, col):
        """Display all the blank and boundary tiles next to blank tiles.

        Parameters:
        row -- integer that denotes the row of the current tile
        col -- integer that denotes the column of the current tile
        """
        if self.mine_board[row][col] != 'M' and (
                self.cell_statuses[row][col] == UNCLICKED):
            self.cell_statuses[row][col] = CLICKED
            self.tiles[row*GRID_HEIGHT + col] = (
                Tile(col*TILE_DIMS, row*TILE_DIMS, self)
            )
            if self.mine_board[row][col] == 0:
                if row - 1 >= 0:
                    self.display_adjacent_tiles(row-1, col)
                    if col - 1 >= 0 and self.mine_board[row-1][col-1] != 'M':
                        self.display_adjacent_tiles(row-1, col-1)
                    if col + 1 <= GRID_WIDTH - 1 and (
                            self.mine_board[row-1][col+1] != 'M'):
                        self.display_adjacent_tiles(row-1, col+1)
                if row + 1 <= GRID_HEIGHT - 1:
                    self.display_adjacent_tiles(row+1, col)
                    if col - 1 >= 0 and self.mine_board[row+1][col-1] != 'M':
                        self.display_adjacent_tiles(row+1, col-1)
                    if col + 1 <= GRID_WIDTH - 1 and (
                            self.mine_board[row+1][col+1] != 'M'):
                        self.display_adjacent_tiles(row+1, col+1)
                if col - 1 >= 0:
                    self.display_adjacent_tiles(row, col-1)
                if col + 1 <= GRID_WIDTH - 1:
                    self.display_adjacent_tiles(row, col+1)

    def reveal_board(self):
        """Reveal the entire board."""
        for row, r_val in enumerate(self.cell_statuses):
            for col, _ in enumerate(r_val):
                if self.cell_statuses[row][col] != CLICKED:
                    self.cell_statuses[row][col] = CLICKED
                    self.tiles[row*GRID_HEIGHT + col] = (
                        Tile(col*TILE_DIMS, row*TILE_DIMS, self)
                    )
        self.board_is_complete = True

    def initialize_cell_statuses(self):
        """Initialize all cells as being unclicked."""
        self.cell_statuses = []
        for _ in range(GRID_HEIGHT):
            self.cell_statuses.append([UNCLICKED]*GRID_WIDTH)

    def generate_tiles(self):
        """Draw the initial board that is shown to the player."""
        self.tiles = []
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                self.tiles.append(Tile(j*TILE_DIMS, i*TILE_DIMS, self))

    def initialize_hidden_board(self):
        """Initialize the hidden board as all blanks."""
        self.mine_board = []
        for _ in range(GRID_HEIGHT):
            self.mine_board.append([0]*GRID_WIDTH)

    def place_mines(self):
        """Place the mines inside the board randomly."""
        total_mines_to_place = self.mines_left
        while total_mines_to_place > 0:
            rand_x = random.choice(range(GRID_HEIGHT))
            rand_y = random.choice(range(GRID_WIDTH))
            if self.mine_board[rand_x][rand_y] == 0:
                self.mine_board[rand_x][rand_y] = 'M'
                total_mines_to_place -= 1

    def add_hint_numbers(self):
        """Add the hint numbers to the board."""
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.mine_board[i][j] == 'M':
                    if i - 1 >= 0:
                        if j - 1 >= 0 and self.mine_board[i-1][j-1] != 'M':
                            self.mine_board[i-1][j-1] += 1
                        if j + 1 <= GRID_WIDTH - 1 and (
                                self.mine_board[i-1][j+1] != 'M'):
                            self.mine_board[i-1][j+1] += 1
                        if self.mine_board[i-1][j] != 'M':
                            self.mine_board[i-1][j] += 1
                    if i + 1 <= GRID_HEIGHT - 1:
                        if j - 1 >= 0 and self.mine_board[i+1][j-1] != 'M':
                            self.mine_board[i+1][j-1] += 1
                        if j + 1 <= GRID_WIDTH - 1 and (
                                self.mine_board[i+1][j+1] != 'M'):
                            self.mine_board[i+1][j+1] += 1
                        if self.mine_board[i+1][j] != 'M':
                            self.mine_board[i+1][j] += 1
                    if j - 1 >= 0 and self.mine_board[i][j-1] != 'M':
                        self.mine_board[i][j-1] += 1
                    if j + 1 <= GRID_WIDTH - 1 and (
                            self.mine_board[i][j+1] != 'M'):
                        self.mine_board[i][j+1] += 1

    def cell_is_clicked(self, mouse_x_loc, mouse_y_loc):
        """Perform appropriate actions when the user left clicks a cell.

        Parameters:
        mouse_x_loc -- the x coordinate of the mouse when left clicked
        mouse_y_loc -- the y coordinate of the mouse when left clicked

        Returns:
        make_new_cell -- boolean for if a new cell should be constructed
        """
        if self.cell_statuses[mouse_x_loc][mouse_y_loc] == UNCLICKED:
            if self.mine_board[mouse_x_loc][mouse_y_loc] == 'M':
                self.game_is_lost()
            elif self.mine_board[mouse_x_loc][mouse_y_loc] == 0:
                self.display_adjacent_tiles(mouse_x_loc, mouse_y_loc)
            else:
                self.cell_statuses[mouse_x_loc][mouse_y_loc] = CLICKED
            make_new_cell = True
        else:
            make_new_cell = False
        return make_new_cell

    def cell_is_flagged(self, mouse_x_loc, mouse_y_loc):
        """Perform appropriate actions when the user right clicks a cell.

        Parameters:
        mouse_x_loc -- the x coordinate of the mouse when right clicked
        mouse_y_loc -- the y coordinate of the mouse when right clicked

        Returns:
        make_new_cell -- boolean for if a new cell should be constructed
        """
        if self.cell_statuses[mouse_x_loc][mouse_y_loc] == UNCLICKED and (
                self.mines_left > 0):
            self.cell_statuses[mouse_x_loc][mouse_y_loc] = FLAGGED
            self.mines_left -= 1
            make_new_cell = True
        elif self.cell_statuses[mouse_x_loc][mouse_y_loc] == FLAGGED:
            self.cell_statuses[mouse_x_loc][mouse_y_loc] = UNCLICKED
            self.mines_left += 1
            make_new_cell = True
        else:
            make_new_cell = False
        return make_new_cell

    def construct_cell(self, mouse_x_loc, mouse_y_loc):
        """Construct a new cell for when its state has changed.

        Parameters:
        mouse_x_loc -- the x coordinate of the new cell on the board
        mouse_y_loc -- the y coordinate of the new cell on the board
        """
        self.tiles[mouse_x_loc*GRID_HEIGHT + mouse_y_loc] = (
            Tile(mouse_y_loc*TILE_DIMS, mouse_x_loc*TILE_DIMS, self)
        )

    def check_for_win(self):
        """Determine if the player won the game."""
        if not self.board_is_complete and self.mines_left == 0 and (
                all(x != UNCLICKED for y in self.cell_statuses for x in y)):
            self.game_is_won()

    def game_is_lost(self):
        """Perform actions for when the game was lost."""
        self.reveal_board()
        self.mines_left = 0
        EXPLOSION_SOUND.play()
        self.result = 'You lost!\nTry again!'

    def game_is_won(self):
        """Perform actions for when the game was won."""
        self.board_is_complete = True
        WINNER_SOUND.play()
        self.result = 'You won!\nPlay again!'


def start_new_game():
    """Begin a new game."""
    board.__init__()

# Construct a Game object so the game can start
Game(
    width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
    window_text='Minesweeper by Dan Tinsley', grab_input=True,
    collision_events_enabled=False
)

# Create fonts
DESCRIPTION_FONT = (
    sge.gfx.Font(name='fonts/horta.ttf', size=36, underline=True)
)
MINES_LEFT_FONT = sge.gfx.Font(name='fonts/horta.ttf', size=60)
INSTRUCTIONS_FONT = sge.gfx.Font(name='fonts/horta.ttf', size=18)
GAME_OVER_FONT = sge.gfx.Font(name='fonts/horta.ttf', size=50)

# Create sound effect
EXPLOSION_SOUND = sge.snd.Sound('sounds/explosion.ogg')
WINNER_SOUND = sge.snd.Sound('sounds/winner.ogg')

# Create sprites
UNCLICKED_TILE_SPRITE = (
    sge.gfx.Sprite(width=TILE_DIMS, height=TILE_DIMS, origin_x=0, origin_y=0)
)
CLICKED_TILE_SPRITE = (
    sge.gfx.Sprite(width=TILE_DIMS, height=TILE_DIMS, origin_x=0, origin_y=0)
)
FLAGGED_TILE_SPRITE = (
    sge.gfx.Sprite(
        name='flag', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
MINE_SPRITE = (
    sge.gfx.Sprite(
        name='explosion', directory='images/', width=TILE_DIMS,
        height=TILE_DIMS, origin_x=0, origin_y=0
    )
)
NUMBER_1_SPRITE = (
    sge.gfx.Sprite(
        name='one', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_2_SPRITE = (
    sge.gfx.Sprite(
        name='two', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_3_SPRITE = (
    sge.gfx.Sprite(
        name='three', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_4_SPRITE = (
    sge.gfx.Sprite(
        name='four', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_5_SPRITE = (
    sge.gfx.Sprite(
        name='five', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_6_SPRITE = (
    sge.gfx.Sprite(
        name='six', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_7_SPRITE = (
    sge.gfx.Sprite(
        name='seven', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)
NUMBER_8_SPRITE = (
    sge.gfx.Sprite(
        name='eight', directory='images/', width=TILE_DIMS, height=TILE_DIMS,
        origin_x=0, origin_y=0
    )
)

# List of the 8 number sprites
NUMBER_TILES = [
    NUMBER_1_SPRITE, NUMBER_2_SPRITE, NUMBER_3_SPRITE, NUMBER_4_SPRITE,
    NUMBER_5_SPRITE, NUMBER_6_SPRITE, NUMBER_7_SPRITE, NUMBER_8_SPRITE
]

# Create tiles using the sprites
UNCLICKED_TILE_SPRITE.draw_rectangle(
    0, 0, UNCLICKED_TILE_SPRITE.width, UNCLICKED_TILE_SPRITE.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("red")
)
CLICKED_TILE_SPRITE.draw_rectangle(
    0, 0, CLICKED_TILE_SPRITE.width, CLICKED_TILE_SPRITE.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color("white")
)
FLAGGED_TILE_SPRITE.draw_rectangle(
    0, 0, FLAGGED_TILE_SPRITE.width, FLAGGED_TILE_SPRITE.height,
    outline=sge.gfx.Color("black"), fill=sge.gfx.Color((100, 100, 100, 100))
)
MINE_SPRITE.draw_rectangle(
    0, 0, MINE_SPRITE.width, MINE_SPRITE.height, outline=sge.gfx.Color("black")
)
for number_tile in NUMBER_TILES:
    number_tile.draw_rectangle(
        0, 0, number_tile.width, number_tile.height,
        outline=sge.gfx.Color("black")
    )

# Instantiate the board for gameplay
board = Board()

# Instantiate the level with a specified background
BACKGROUND = sge.gfx.Background([], sge.gfx.Color("white"))
sge.game.start_room = Room([], background=BACKGROUND)

# Make the mouse visible for usage in the game
sge.game.mouse.visible = True

if __name__ == '__main__':
    sge.game.start()
