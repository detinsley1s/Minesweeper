import sge


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    pass


Game(width=800, height=600, window_text='Minesweeper by Dan Tinsley', collision_events_enabled=False)

background = sge.gfx.Background([], sge.gfx.Color("white"))
sge.game.start_room = Room(background=background)

sge.game.start()
