from config.settings import DRONE_DIST

class Movement:
    def __init__(self, tello):
        self.tello = tello

    def move_forward(self):
        self.tello.move_forward(DRONE_DIST)

    def move_back(self):
        self.tello.move_back(DRONE_DIST)

    def move_left(self):
        self.tello.move_left(DRONE_DIST)

    def move_right(self):
        self.tello.move_right(DRONE_DIST)

    def move_up(self):
        self.tello.move_up(DRONE_DIST)

    def move_down(self):
        self.tello.move_down(DRONE_DIST)