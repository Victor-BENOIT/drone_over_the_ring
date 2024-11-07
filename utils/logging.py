from config.settings import LOGGING_ENABLED
import os

class Logging:
    def __init__(self):
        self.movements = []
        self.filename = 'log.txt'
        if not LOGGING_ENABLED:
            if os.path.exists(self.filename):
                os.remove(self.filename)

    def add_movement(self, direction, value):
        if not LOGGING_ENABLED:
            return
        if direction in ['up', 'down', 'right', 'left', 'forward', 'backward', 'rotate_clockwise', 'rotate_counter_clockwise']:
            self.movements.append((direction, value))
        else:
            print("Invalid direction. Must be one of 'up', 'down', 'right', 'left', 'forward', 'backward', 'rotate_clockwise', 'rotate_counter_clockwise'.")
        
    def add_gate_marker(self, gate_type):
        if not LOGGING_ENABLED:
            return
        if gate_type in ['hoop', 'hex', 'square']:
            self.movements.append(("GATE_IN_FRONT", gate_type))
        else:
            print("Invalid gate type. Must be one of 'hoop', 'hex', 'square'.")

    def reduce_movements(self):
        reduced_movements = []
        if not self.movements:
            return reduced_movements

        current_direction_values = {}

        for direction, value in self.movements:
            if direction == "GATE_IN_FRONT":
                for dir, val in current_direction_values.items():
                    reduced_movements.append((dir, val))
                reduced_movements.append((direction, value))
                current_direction_values = {}
            else:
                if direction in current_direction_values:
                    current_direction_values[direction] += value
                else:
                    current_direction_values[direction] = value

        for dir, val in current_direction_values.items():
            reduced_movements.append((dir, val))

        self.movements = reduced_movements

    def save_logs(self):
        if not LOGGING_ENABLED:
            return
        self.reduce_movements()
        with open(self.filename, 'w') as file:
            for direction, value in self.movements:
                file.write(f"{direction} {value}\n")