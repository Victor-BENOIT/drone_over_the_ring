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
        if direction in ['up', 'down', 'right', 'left', 'forward', 'backward']:
            self.movements.append((direction, value))
        else:
            raise ValueError("Invalid direction. Must be one of 'up', 'down', 'right', 'left', 'forward', 'backward'.")

    def reduce_movements(self):
        if not LOGGING_ENABLED:
            return
        
        reduced_movements = []
        current_direction, current_value = self.movements[0]

        for direction, value in self.movements[1:]:
            if direction == current_direction:
                current_value += value
            else:
                reduced_movements.append((current_direction, current_value))
                current_direction, current_value = direction, value
        reduced_movements.append((current_direction, current_value))
        self.movements = reduced_movements

    def log_movements(self):
        if not LOGGING_ENABLED:
            return
        with open(self.filename, 'w') as file:
            for direction, value in self.movements:
                file.write(f"{direction}: {value}\n")