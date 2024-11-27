from config.settings import DRONE_DIST, MOVE_CROSS_GATE, SCREEN_WIDTH, DEAD_ZONE_SCAN

class Movement:
    """
    Classe pour gérer les mouvements du drone et enregistrer les actions dans le logging.

    Attributes:
        controller: L'objet contrôleur pour gérer les interactions avec le drone et le logging.
        tello: Instance de contrôle du drone.
        logging: Instance pour enregistrer les mouvements.
    """

    def __init__(self, controller):
        """
        Initialise la classe Movement avec un contrôleur.

        Args:
            controller: L'objet contrôleur contenant les instances du drone et du logging.
        """
        self.controller = controller
        self.tello = controller.tello
        self.logging = controller.logging

    def move_forward(self, distance=DRONE_DIST):
        """
        Déplace le drone vers l'avant et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir en avant (par défaut : DRONE_DIST).
        """
        self.tello.move_forward(distance)
        self.logging.add_movement('forward', distance)

    def move_backward(self, distance=DRONE_DIST):
        """
        Déplace le drone vers l'arrière et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir en arrière (par défaut : DRONE_DIST).
        """
        self.tello.move_back(distance)
        self.logging.add_movement('backward', distance)

    def move_left(self, distance=DRONE_DIST):
        """
        Déplace le drone vers la gauche et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir à gauche (par défaut : DRONE_DIST).
        """
        self.tello.move_left(distance)
        self.logging.add_movement('left', distance)

    def move_right(self, distance=DRONE_DIST):
        """
        Déplace le drone vers la droite et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir à droite (par défaut : DRONE_DIST).
        """
        self.tello.move_right(distance)
        self.logging.add_movement('right', distance)

    def move_up(self, distance=DRONE_DIST):
        """
        Déplace le drone vers le haut et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir vers le haut (par défaut : DRONE_DIST).
        """
        self.tello.move_up(distance)
        self.logging.add_movement('up', distance)

    def move_down(self, distance=DRONE_DIST):
        """
        Déplace le drone vers le bas et enregistre le mouvement.

        Args:
            distance (int): La distance à parcourir vers le bas (par défaut : DRONE_DIST).
        """
        self.tello.move_down(distance)
        self.logging.add_movement('down', distance)

    def rotate_clockwise(self, angle):
        """
        Fait pivoter le drone dans le sens horaire et enregistre le mouvement.

        Args:
            angle (int): L'angle en degrés pour la rotation dans le sens horaire.
        """
        self.tello.rotate_clockwise(angle)
        self.logging.add_movement('rotate_clockwise', angle)

    def rotate_counter_clockwise(self, angle):
        """
        Fait pivoter le drone dans le sens antihoraire et enregistre le mouvement.

        Args:
            angle (int): L'angle en degrés pour la rotation dans le sens antihoraire.
        """
        self.tello.rotate_counter_clockwise(angle)
        self.logging.add_movement('rotate_counter_clockwise', angle)

    def cross_gate(self, distance, type):
        """
        Fait traverser une porte par le drone en ajustant la rotation selon le type de porte.

        Args:
            distance (int): La distance pour traverser la porte.
            type (str): Le type de porte, soit "hoop" ou "hex", définissant la rotation.
        """
        self.logging.add_gate_marker(type)
        self.tello.move_forward(distance + MOVE_CROSS_GATE)
        self.logging.add_movement('forward', distance + MOVE_CROSS_GATE)
        if type == "hoop":
            self.rotate_clockwise(110)
        elif type == "hex":
            self.rotate_counter_clockwise(110)

        self.controller.mode.locked_vertical = False
        self.controller.mode.locked_horizontal = False
        self.controller.mode.locked_distance = False

        # self.sweeping_for_gates(type)
            
    
    # def sweeping_for_gates(self, type):
    #     increment = 10
    #     x, _, w, _, _, type = self.controller.vision.gates[0]
    #     if type == "hoop":
    #         self.rotate_clockwise(increment)
    #         if self.vision.distance is not None and ((SCREEN_WIDTH / 2 - DEAD_ZONE_SCAN) < (x + w / 2) < (SCREEN_WIDTH / 2 + DEAD_ZONE_SCAN)):
    #             return
    #         else:
    #             self.sweeping_for_gates(self.type)
    #     elif type == "hex":
    #         self.rotate_counter_clockwise(increment)
    #     angle += increment
        
