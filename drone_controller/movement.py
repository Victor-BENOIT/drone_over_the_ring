from config.settings import DRONE_DIST

class Movement:
    def __init__(self, drone_controller):
        self.drone_controller = drone_controller
        self.tello = drone_controller.tello
        self.logging = drone_controller.logging

    def move_forward(self, distance = DRONE_DIST):
        self.tello.move_forward(distance)

    def move_backward(self, distance = DRONE_DIST):
        self.tello.move_back(distance)

    def move_left(self, distance = DRONE_DIST):
        self.tello.move_left(distance)

    def move_right(self, distance = DRONE_DIST):
        self.tello.move_right(distance)

    def move_up(self, distance = DRONE_DIST):
        self.tello.move_up(distance)

    def move_down(self, distance = DRONE_DIST):
        self.tello.move_down(distance)