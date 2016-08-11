import sge


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    pass


Game(window_text='Minesweeper by Dan Tinsley', collision_events_enabled=False)

sge.game.start_room = Room()

sge.game.start()
