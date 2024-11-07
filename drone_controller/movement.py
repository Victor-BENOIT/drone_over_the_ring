from config.settings import DRONE_DIST

class Movement:
    def __init__(self, controller):
        self.controller = controller
        self.tello = controller.tello
        self.logging = controller.logging

    def move_forward(self, distance = DRONE_DIST):
        self.tello.move_forward(distance)
        self.logging.add_movement('forward', distance)

    def move_backward(self, distance = DRONE_DIST):
        self.tello.move_back(distance)
        self.logging.add_movement('backward', distance)

    def move_left(self, distance = DRONE_DIST):
        self.tello.move_left(distance)
        self.logging.add_movement('left', distance)

    def move_right(self, distance = DRONE_DIST):
        self.tello.move_right(distance)
        self.logging.add_movement('right', distance)

    def move_up(self, distance = DRONE_DIST):
        self.tello.move_up(distance)
        self.logging.add_movement('up', distance)

    def move_down(self, distance = DRONE_DIST):
        self.tello.move_down(distance)
        self.logging.add_movement('down', distance)

    def rotate_clockwise(self, angle):
        self.tello.rotate_clockwise(angle)
        self.logging.add_movement('rotate_clockwise', angle)

    def rotate_counter_clockwise(self, angle):
        self.tello.rotate_counter_clockwise(angle)
        self.logging.add_movement('rotate_counter_clockwise', angle)

    def cross_gate(self, distance, type):
        self.logging.add_gate_marker(type)
        self.tello.move_forward(distance + 100)
        if type == "hoop":
            self.rotate_clockwise(110)
        elif type == "hex":
            self.rotate_counter_clockwise(110)

        self.controller.mode.locked_vertical = False
        self.controller.mode.locked_horizontal = False
        self.controller.mode.locked_distance = False