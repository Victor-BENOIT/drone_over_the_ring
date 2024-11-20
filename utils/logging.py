from config.settings import LOGGING_ENABLED
import os

class Logging:
    """
    Classe de logging des mouvements du drone.

    Attributes:
        movements: Liste des mouvements enregistrés.
        filename: Nom du fichier de log.
    """

    def __init__(self):
        """
        Initialise l'instance de logging, crée un fichier de log si LOGGING_ENABLED est activé.
        Supprime tout fichier de log existant si LOGGING_ENABLED est désactivé.
        """
        self.movements = []
        self.filename = os.path.join(os.path.dirname(__file__), 'log.txt')
        if not LOGGING_ENABLED:
            if os.path.exists(self.filename):
                os.remove(self.filename)

    def add_movement(self, direction, value):
        """
        Ajoute un mouvement à la liste si la direction est valide et LOGGING_ENABLED est activé.

        Args:
            direction: La direction du mouvement, doit être parmi ['up', 'down', 'right', 'left', 'forward', 'backward', 'rotate_clockwise', 'rotate_counter_clockwise'].
            value: La valeur du mouvement (par exemple, la distance ou l'angle).
        """
        if not LOGGING_ENABLED:
            return
        if direction in ['up', 'down', 'right', 'left', 'forward', 'backward', 'rotate_clockwise', 'rotate_counter_clockwise']:
            self.movements.append((direction, value))
        else:
            print("Invalid direction. Must be one of 'up', 'down', 'right', 'left', 'forward', 'backward', 'rotate_clockwise', 'rotate_counter_clockwise'.")
        
    def add_gate_marker(self, gate_type):
        """
        Ajoute un marqueur de porte à la liste si le type de porte est valide et LOGGING_ENABLED est activé.

        Args:
            gate_type: Le type de porte, doit être parmi ['hoop', 'hex', 'square'].
        """
        if not LOGGING_ENABLED:
            return
        if gate_type in ['hoop', 'hex', 'square']:
            self.movements.append(("GATE_IN_FRONT", gate_type))
        else:
            print("Invalid gate type. Must be one of 'hoop', 'hex', 'square'.")

    def reduce_movements(self):
        """
        Réduit la liste des mouvements en combinant les mouvements consécutifs dans la même direction.
        """
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
        """
        Sauvegarde les mouvements réduits dans un fichier de log si LOGGING_ENABLED est activé.
        """
        if not LOGGING_ENABLED:
            return
        self.reduce_movements()
        with open(self.filename, 'w') as file:
            for direction, value in self.movements:
                file.write(f"{direction} {value}\n")
