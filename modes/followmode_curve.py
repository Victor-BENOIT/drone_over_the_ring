import re
from djitellopy import Tello
import math

LOG_PATH = "log_test_curve.txt"
POIDS_RECTIFICATION = False
DRONE_ACTIVATED = True


class DronePathCalculator:
    def __init__(self, log_path):
        self.log_path = log_path
        self.mouvements = []
        self.matrice_coordonnees = []  # Matrice pour stocker les coordonnées
        self.coordonnees_porte = (None, None, None)
        self.gate_types = []
        if DRONE_ACTIVATED:
            self.tello = Tello()

    def lecture_log(self):
        """Lecture du fichier log pour extraire les mouvements."""
        with open(self.log_path, 'r') as file:
            for line in file:
                line = line.strip()
                if re.match(r'^(up|down|forward|backward|left|right|rotate_counter_clockwise|rotate_clockwise) \d+', line):
                    mouvement, valeur = line.split()
                    valeur = int(valeur)

                    # Appliquer la rectification si nécessaire
                    if POIDS_RECTIFICATION:
                        if mouvement == "forward":
                            valeur = int(valeur * 0.5)
                        if mouvement == "up":
                            valeur = int(valeur * 0.5)

                    self.mouvements.append([mouvement, valeur])

                elif line.startswith("GATE_IN_FRONT"):
                    _, gate_type = line.split()
                    self.mouvements.append(["GATE_IN_FRONT", None, gate_type])

    def calculer_coordonnees(self):
        """Calcule les coordonnées finales avant chaque porte."""
        x, y, z = 0, 0, 0

        for movement in self.mouvements:
            if movement[0] == "GATE_IN_FRONT":
                # Sauvegarder les coordonnées avant la porte et réinitialiser les coordonnées
                self.matrice_coordonnees.append((x, y, z))
                self.gate_types.append(movement[2])
                x, y, z = 0, 0, 0  # Réinitialisation des coordonnées après chaque porte
            else:
                direction, value = movement
                if direction == "forward":
                    x += value
                elif direction == "backward":
                    x -= value
                elif direction == "left":
                    y += value
                elif direction == "right":
                    y -= value
                elif direction == "up":
                    z += value
                elif direction == "down":
                    z -= value

    def calculer_distance(self, x1, y1, z1, x2, y2, z2):
            return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2), 2)

    def afficher_coordonnees(self):
        """Affiche les coordonnées calculées."""
        for i, coord in enumerate(self.matrice_coordonnees):
            x, y, z = coord
            print(f"Coordonnées avant la porte {self.gate_types[i]}: x={x}, y={y}, z={z}")

    def effectuer_mouvement(self, position_porte, gate_type):
        x_target, y_target, z_target = position_porte

        dist = self.calculer_distance(x_target, y_target, z_target, 0, 0, 0)
        print(dist)

        # Calcul du point du milieu
        x_middle = int((x_target) / 2)
        y_middle = int((y_target) / 2)
        z_middle = int((z_target) / 2 + int(dist / 20))

        vitesse = 60

        if DRONE_ACTIVATED:
            print(f"Coordonnées de la target: x={x_target}, y={y_target}, z={z_target}")
            print(f"Coordonnées du point du milieu: x={x_middle}, y={y_middle}, z={z_middle}")

            # 1. Déplacement vers le point du milieu
            self.tello.curve_xyz_speed(x_middle, y_middle, z_middle, x_target, y_target, z_target, vitesse)

            # 2. Avancer de 150
            self.tello.move_forward(150)

            # 3. Tourner à gauche ou à droite de 110° selon le type de porte
            if gate_type == "hex":
                self.tello.rotate_counter_clockwise(110)
            elif gate_type == "hoop":
                self.tello.rotate_clockwise(110)

    def run(self):
        """Exécution complète du calcul."""
        self.lecture_log()
        self.calculer_coordonnees()
        self.afficher_coordonnees()

        print(self.matrice_coordonnees)

        if DRONE_ACTIVATED:
            self.tello.connect()
            self.tello.takeoff()
            self.tello.move_up(110 - self.tello.get_height())

        # Effectuer les mouvements en fonction des coordonnées calculées
        for i, coord in enumerate(self.matrice_coordonnees):
            gate_type = self.gate_types[i]
            self.effectuer_mouvement(coord, gate_type)

        if DRONE_ACTIVATED:
            self.tello.land()


if __name__ == "__main__":
    calculator = DronePathCalculator(LOG_PATH)
    calculator.run()
