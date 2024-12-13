import re
from djitellopy import Tello
import math
from followmode_settings import LOG_PATH, DRONE_ACTIVATED, AVERAGE_STRATING_HEIGHT

class DronePathCalculator:
    def __init__(self, log_path):
        self.log_path = log_path
        self.mouvements = []
        self.matrice_coordonnees = []  # Matrice pour stocker les coordonnées
        self.coordonnees_porte = (None, None, None)
        self.gate_types = []
        self.angle = 90 #cartésiennes
        self.coord_cart = [
            ["point", [(0, 0, AVERAGE_STRATING_HEIGHT)]]
            ]
        self.gates_cart = []
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
            return round(math.sqrt((x2 - x1)**2 + (y1 - y1)**2 + (z2 - z1)**2), 2)

    def afficher_coordonnees(self):
        """Affiche les coordonnées calculées."""
        for i, coord in enumerate(self.matrice_coordonnees):
            x, y, z = coord
            print(f"Coordonnées relatives avant la porte {self.gate_types[i]}: x={x}, y={y}, z={z}")

    def creation_path_cartesien(self):

        for i, coord in enumerate(self.matrice_coordonnees):
            gate_type = self.gate_types[i]

            x_target, y_target, z_target = coord

            dist = self.calculer_distance(x_target, y_target, z_target, 0, 0, 0)

            # Calcul du point du milieu
            x_middle = int((x_target) / 2)
            y_middle = int((y_target) / 2)
            z_middle = int((z_target) / 2 + int(dist / 20))

            # Ajout des coordonnées cartésiennes
            self.ajout_coordonnees_cartesiennes(
                "curve", 
                coord_middle=(x_middle, y_middle, z_middle), 
                coord_target=(x_target, y_target, z_target))
            
            self.ajout_gate_cartesien(gate_type)
            
            self.ajout_coordonnees_cartesiennes(
                "straight line", 
                axe="x", 
                distance = 150)
            
            if gate_type == "hex":
                self.angle += 90
            elif gate_type == "hoop":
                self.angle -= 90

    def ajout_coordonnees_cartesiennes(self, type_mouvement, coord_middle=None, coord_target=None, axe=None, distance=None):
        # Déterminer le point de départ
        coord_start = None
        if self.coord_cart[-1][0] == "point":
            coord_start = list(self.coord_cart[-1][1])[0]
        elif self.coord_cart[-1][0] == "straight line":
            coord_start = list(self.coord_cart[-1][1])[1]
        elif self.coord_cart[-1][0] == "curve":
            coord_start = list(self.coord_cart[-1][1])[2]

        x_start, y_start, z_start = coord_start

        # Si l'angle n'existe pas encore, initialiser à 90° (facing X+ axis)
        if not hasattr(self, "angle"):
            self.angle = 90

        if type_mouvement == "curve":
            if coord_middle is None or coord_target is None:
                raise ValueError("coord_middle et coord_target doivent être fournis pour un mouvement 'curve'.")

            # Calculer les coordonnées des points intermédiaire et final en fonction de l'angle
            x_middle, y_middle, z_middle = coord_middle
            x_target, y_target, z_target = coord_target

            # Calcul des coordonnées globales en fonction de l'angle
            middle_global = (
                round(x_start + x_middle * math.cos(math.radians(self.angle)) - y_middle * math.sin(math.radians(self.angle))),
                round(y_start + x_middle * math.sin(math.radians(self.angle)) + y_middle * math.cos(math.radians(self.angle))),
                round(z_start + z_middle)
            )

            target_global = (
                round(x_start + x_target * math.cos(math.radians(self.angle)) - y_target * math.sin(math.radians(self.angle))),
                round(y_start + x_target * math.sin(math.radians(self.angle)) + y_target * math.cos(math.radians(self.angle))),
                round(z_start + z_target)
            )

            # Stockage des données dans le bon ordre (x, y, z)
            self.coord_cart.append([
                "curve", 
                [
                    (x_start, y_start, z_start),  # point de départ
                    middle_global,  # point intermédiaire
                    target_global   # point cible
                ]
            ])

        elif type_mouvement == "straight line":
            if axe is None or distance is None:
                raise ValueError("axe et distance doivent être fournis pour un mouvement 'straight line'.")

            # Calculer la nouvelle position en ligne droite en fonction de l'angle
            if axe == "x":
                dx = round(distance * math.cos(math.radians(self.angle)))
                dy = round(distance * math.sin(math.radians(self.angle)))
                new_coord = (round(x_start + dx), round(y_start + dy), round(z_start))
            elif axe == "y":
                # Mouvement sur l'axe Y sans angle
                new_coord = (round(x_start), round(y_start + distance), round(z_start))
            elif axe == "z":
                # Mouvement sur l'axe Z sans impact d'angle
                new_coord = (round(x_start), round(y_start), round(z_start + distance))
            else:
                raise ValueError("axe doit être 'x', 'y' ou 'z'.")

            # Stockage des coordonnées dans le bon ordre (x, y, z)
            self.coord_cart.append([
                "straight line",
                [
                    (x_start, y_start, z_start),  # point de départ
                    new_coord  # point d'arrivée
                ]
            ])

    def ajout_gate_cartesien(self, gate_type):

        coord_start = None
        if self.coord_cart[-1][0] == "point":
            coord_start = list(self.coord_cart[-1][1])[0]
        elif self.coord_cart[-1][0] == "straight line":
            coord_start = list(self.coord_cart[-1][1])[1]
        elif self.coord_cart[-1][0] == "curve":
            coord_start = list(self.coord_cart[-1][1])[2]
        
        x, y, z = coord_start
        distance_gate = 50

        x += round(distance_gate * math.cos(math.radians(self.angle)))
        y += round(distance_gate * math.sin(math.radians(self.angle)))

        self.gates_cart.append([gate_type, self.angle, [x, y, z]])
            
    def effectuer_mouvements_drone(self):
        # Effectuer les mouvements en fonction des coordonnées calculées
        for i, coord in enumerate(self.matrice_coordonnees):
            gate_type = self.gate_types[i]
            self.effectuer_mouvement(coord, gate_type)

    def effectuer_mouvement(self, position_porte, gate_type):
            x_target, y_target, z_target = position_porte

            dist = self.calculer_distance(x_target, y_target, z_target, 0, 0, 0)

            # Calcul du point du milieu
            x_middle = int((x_target) / 2)
            y_middle = int((y_target) / 2)
            z_middle = int((z_target) / 2 + int(dist / 20))

            if DRONE_ACTIVATED:
                vitesse = 60

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
        self.creation_path_cartesien()

        print(self.mouvements)
        print(self.matrice_coordonnees)
        print(self.coord_cart)
        print(self.gates_cart)

        if DRONE_ACTIVATED:
            self.tello.connect()
            self.tello.takeoff()
            self.tello.move_up(110 - self.tello.get_height())

        self.effectuer_mouvements_drone()

        if DRONE_ACTIVATED:
            self.tello.land()


if __name__ == "__main__":
    calculator = DronePathCalculator(LOG_PATH)
    calculator.run()
