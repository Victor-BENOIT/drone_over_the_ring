from drone_controller.keyboard_control import Keyboard
from math import sqrt
from config.settings import TARGET_DIST, DEAD_ZONE, MOVE_RATIO,SCREEN_WIDTH, DEAD_ZONE_SCAN
import time

class IdleMode:
    def __init__(self, controller):
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision

    def start(self):
        print("Mode Idle activé.")

    def main_loop(self):
        return  # Ne fait rien en mode Idle

    def stop(self):
        return  # Ne fait rien en mode Idle

class ManualMode:
    def __init__(self, controller):
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision
        self.keyboard = Keyboard(self.controller)

    def start(self):
        print("Mode manuel activé.\nZQSD pour mouvement, A pour monter, E pour descendre, O pour décollage/atterrissage.")
        self.keyboard.start_listening()

    def main_loop(self):
        #print(self.vision.distance)
        return  #Ne fait rien d'automatique en manual mode

    def stop(self):
        self.keyboard.stop_listening()
        if self.controller.is_flying():
            self.controller.land()

class AutonomousMode:
    def __init__(self, controller):
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision
        self.locked_horizontal = False
        self.locked_vertical = False
        self.locked_distance = False
        self.gates_passed = 0

    def start(self):
        print("Mode autonome activé.")
        if not self.controller.is_flying():
            self.controller.takeoff()
        self.controller.movement.move_up(130 - self.tello.get_height())

    def main_loop(self):
        # print("LOCK: " + str(self.locked_horizontal) + " " + str(self.locked_vertical) + " " + str(self.locked_distance))
        if self.gates_passed == 2:
            self.controller.land()
            return
        
        print(self.vision.gates)

        if self.locked_horizontal == True & self.locked_vertical == True & self.locked_distance == True:
            self.controller.movement.cross_gate(int(self.vision.distance), self.vision.gates[0][5])
            # self.controller.movement.move_forward(100)
            self.gates_passed += 1
        else :
            self.horizontal_vertical_tracking()
            self.distance_tracking()

    def stop(self):
        if self.controller.is_flying():
            self.controller.land()

    def horizontal_vertical_tracking(self):
        list = self.vision.get_gates(self.controller.get_frame())
        if len(list) == 1:
            (x, y, w, h, score, class_id) = list[0]
            x_center_box = x + w / 2
            y_center_box = y + h / 2

            x_corner, y_corner, w_width, w_height = self.controller.target.get_target_window()

            min_x_window = x_corner
            max_x_window = x_corner + w_width 
            min_y_window = y_corner 
            max_y_window = y_corner + w_height

            # Vérifier les conditions et ajuster la position du drone
            if y_center_box < min_y_window:  # La target est en dessous de la fenêtre
                self.controller.movement.move_up()
                self.locked_vertical = False 
            elif y_center_box > max_y_window:  # La target est au-dessus de la fenêtre
                self.controller.movement.move_down()
                self.locked_vertical = False 
            else:
                self.locked_vertical = True 

            if x_center_box < min_x_window:  # La target est à gauche de la fenêtre
                self.controller.movement.move_right()
                self.locked_horizontal = False
            elif x_center_box > max_x_window:  # La target est à droite de la fenêtre
                self.controller.movement.move_left()
                self.locked_horizontal = False
            else:
                self.locked_horizontal = True

    
    def distance_tracking(self):
        distance = self.vision.distance
        if distance is None:
            return
        
        distance_to_target = distance - TARGET_DIST

        if distance_to_target > 0:
            if DEAD_ZONE > distance_to_target > 0:
                print("Deadzone")
                self.locked_distance = True
            elif distance_to_target * MOVE_RATIO < 20:
                self.controller.movement.move_forward(20)
                self.locked_distance = False
            else:
                self.controller.movement.move_forward(int(distance_to_target * MOVE_RATIO))
                self.locked_distance = False

        elif distance_to_target < 0:
            if -DEAD_ZONE < distance_to_target < 0:
                print("Deadzone")
                self.locked_distance = True
            elif abs(distance_to_target * MOVE_RATIO) < 20:
                self.controller.movement.move_backward(20)
                self.locked_distance = False
            else:
                self.controller.movement.move_backward(int(abs(distance_to_target * MOVE_RATIO)))
                self.locked_distance = False

        else:
            return

class ScanMode:
    def __init__(self, controller):
        """
        Initialise une instance de ScanMode avec un contrôleur donné.

        Paramètres:
            controller (Controller): Le contrôleur qui gère le drone (tello) et les systèmes de vision.

        Attributs:
            controller (Controller): Le contrôleur du drone.
            tello (Tello): Instance de drone associée au contrôleur.
            vision (Vision): Système de vision pour la détection de distance et de portes.
            angle (int): L'angle actuel de rotation pour le scan.
            increment (int): La valeur d'incrémentation de l'angle de rotation.
            detected_doors_list (list): Liste contenant les informations des portes détectées.
        """
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision  # Utilise la classe Vision qui contient `distance` et `door`
        self.angle = 0  # Attribut pour suivre l'angle
        self.increment = 10  # Incrément de rotation
        self.detected_doors_list = []  # Liste pour stocker toutes les portes détectées
        self.angle_porte = 0

    def start(self):
        """
        Démarre le mode Scan en prenant le contrôle du drone. Si le drone n'est pas en vol,
        il décolle et s'élève jusqu'à une hauteur de 120 cm.
        
        Cette méthode doit être appelée pour lancer la procédure de scan.
        """
        print("Mode Scan activé.")
        if not self.controller.is_flying():
            self.controller.takeoff()
        while self.tello.get_height() < 120:
            self.controller.movement.move_up(50)

    def detect_door(self):
        """
        Détecte les portes visibles dans le champ de vision du drone.
        Si des portes sont détectées par le système de vision (et qu'elles se trouvent
        dans une certaine distance et zone définie), les informations de chaque porte
        sont enregistrées, incluant la distance, l'angle de détection et le type de porte.
        Les portes détectées sont ajoutées à `detected_doors_list`.
        """
        if self.vision.gates:
            x, _, w, h, _, type = self.vision.gates[0]  # Coordonnée x de la première porte détectée
            
            if (
                self.vision.distance is not None 
                and ((SCREEN_WIDTH / 2 - DEAD_ZONE_SCAN) < (x + w / 2) < (SCREEN_WIDTH / 2 + DEAD_ZONE_SCAN))
            ):
                    # Calcul de l'angle de la porte
                ratio = w / h
                max_angle = 90  # Définir l'angle maximum possible
                self.angle_porte = max(0, min(max_angle, (1 - ratio) * max_angle)) * 2
                
                self.detected_door = {
                    "distance": self.vision.distance,
                    "angle camera": self.angle / 1.25,
                    "angle porte": self.angle_porte,
                    "porte": type
                }
                print(f"GOOD - Porte: {type}, Distance: {self.vision.distance}, Angle camera: {self.angle / 1.25}")
                self.detected_doors_list.append(self.detected_door)
                print(self.detected_doors_list)

    def main_loop(self):
        """
        Exécute la boucle principale pour le scan à 360 degrés.

        Cette méthode est conçue pour être appelée régulièrement pour faire progresser le scan.
        À chaque incrément de rotation (par défaut 10 degrés), elle tente de détecter une porte.
        
        Si un tour complet de 360 degrés est atteint, elle arrête le drone.
        """
        if self.angle < (180 * 1.25):
            self.tello.rotate_clockwise(self.increment)
            self.angle += self.increment
            self.detect_door()
        else:
            print("Rotation à 360 degrés terminée")
            self.stop()

    def stop(self):
        """
        Arrête le mode Scan et fait atterrir le drone si celui-ci est en vol.

        Cette méthode termine la procédure de scan et ramène le drone au sol.
        """
        if self.controller.is_flying():
            self.controller.land()




    