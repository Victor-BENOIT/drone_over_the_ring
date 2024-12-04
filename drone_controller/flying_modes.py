from drone_controller.keyboard_control import Keyboard
from math import sqrt
from config.settings import TARGET_DIST, DEAD_ZONE, MOVE_RATIO,SCREEN_WIDTH, DEAD_ZONE_SCAN, STARTING_DRONE_HEIGHT,MAX_GATES_PASSED
import time

class IdleMode:
    """
    Classe pour gérer le mode inactif du drone, sans mouvement automatique.
    
    Attributes:
        controller: Le contrôleur du drone.
        tello: L'objet Tello représentant le drone.
        vision: L'objet Vision pour la détection des portes et obstacles.
    """

    def __init__(self, controller):
        """
        Initialise la classe IdleMode avec le contrôleur du drone.

        Args:
            controller: Le contrôleur du drone.
        """
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision

    def start(self):
        """Active le mode Idle en affichant un message."""
        print("Mode Idle activé.")

    def main_loop(self):
        """Boucle principale en mode Idle, ne fait rien."""
        return

    def stop(self):
        """Désactive le mode Idle, ne fait rien."""
        return

class ManualMode:
    """
    Classe pour gérer le mode manuel du drone, permettant le contrôle avec le clavier.
    
    Attributes:
        controller: Le contrôleur du drone.
        tello: L'objet Tello représentant le drone.
        vision: L'objet Vision pour la détection.
        keyboard: L'objet Keyboard pour la gestion des commandes clavier.
    """

    def __init__(self, controller):
        """
        Initialise la classe ManualMode avec le contrôleur du drone.

        Args:
            controller: Le contrôleur du drone.
        """
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision
        self.keyboard = Keyboard(self.controller)

    def start(self):
        """Active le mode manuel et démarre l'écoute des touches du clavier."""
        print("Mode manuel activé.\nZQSD pour mouvement, A pour monter, E pour descendre, O pour décollage/atterrissage.")
        self.keyboard.start_listening()

    def main_loop(self):
        """Boucle principale en mode manuel, ne fait rien d'automatique."""
        return

    def stop(self):
        """Désactive le mode manuel, arrête l'écoute clavier et atterrit si le drone vole."""
        self.keyboard.stop_listening()
        if self.controller.is_flying():
            self.controller.land()

class AutonomousMode:
    """
    Classe pour gérer le mode autonome du drone avec suivi automatique des portes.
    
    Attributes:
        controller: Le contrôleur du drone.
        tello: L'objet Tello représentant le drone.
        vision: L'objet Vision pour la détection des portes.
        locked_horizontal: Booléen indiquant si le drone est aligné horizontalement.
        locked_vertical: Booléen indiquant si le drone est aligné verticalement.
        locked_distance: Booléen indiquant si le drone est à la bonne distance.
        gates_passed: Nombre de portes franchies.
    """

    def __init__(self, controller):
        """
        Initialise la classe AutonomousMode avec le contrôleur du drone.

        Args:
            controller: Le contrôleur du drone.
        """
        self.controller = controller
        self.tello = controller.tello
        self.vision = controller.vision
        self.locked_horizontal = False
        self.locked_vertical = False
        self.locked_distance = False
        self.gates_passed = 0

    def start(self):
        """Active le mode autonome, décolle le drone et ajuste sa hauteur."""
        print("Mode autonome activé.")
        if not self.controller.is_flying():
            self.controller.takeoff()
        self.controller.movement.move_up(STARTING_DRONE_HEIGHT - self.tello.get_height())

    def main_loop(self):
        """Boucle principale du mode autonome, gère le suivi et franchissement des portes."""
        if self.gates_passed == MAX_GATES_PASSED:
            self.controller.land()
            return
        
        print(self.vision.gates)

        if self.locked_horizontal and self.locked_vertical and self.locked_distance:
            self.controller.movement.cross_gate(int(self.vision.distance), self.vision.gates[0][5])
            self.gates_passed += 1
        else:
            self.horizontal_vertical_tracking()
            self.distance_tracking()

    def stop(self):
        """Arrête le mode autonome en atterrissant le drone s'il est en vol."""
        if self.controller.is_flying():
            self.controller.land()

    def horizontal_vertical_tracking(self):
        """Gère le suivi horizontal et vertical pour aligner le drone sur une porte détectée."""
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

            if y_center_box < min_y_window:
                self.controller.movement.move_up()
                self.locked_vertical = False 
            elif y_center_box > max_y_window:
                self.controller.movement.move_down()
                self.locked_vertical = False 
            else:
                self.locked_vertical = True 

            if x_center_box < min_x_window:
                self.controller.movement.move_right()
                self.locked_horizontal = False
            elif x_center_box > max_x_window:
                self.controller.movement.move_left()
                self.locked_horizontal = False
            else:
                self.locked_horizontal = True

    def distance_tracking(self):
        """Gère le suivi de distance pour maintenir le drone à la bonne distance d'une porte."""
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

class ScanMode:
    """
    Classe pour gérer le mode de scan du drone, réalisant une rotation pour détecter les portes.

    Attributes:
        controller: Le contrôleur du drone.
        tello: L'objet Tello représentant le drone.
        vision: L'objet Vision pour la détection des portes.
        angle: Angle actuel de rotation du drone.
        increment: Incrément d'angle pour chaque rotation.
        detected_doors_list: Liste des portes détectées.
    """

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
        # Vérifie si le drone est toujours en vol
        if not self.controller.is_flying():
            print("Le drone a atterri. Arrêt du programme.")
            return  # Quitte la méthode si le drone est au sol
        
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
        self.save_detected_doors()
        if self.controller.is_flying():
            self.controller.land()
    
    def save_detected_doors(self):
        """
        Sauvegarde la liste des portes détectées dans un fichier texte.

        Le fichier est nommé 'detected_doors.txt' et est généré dans le répertoire courant.
        """
        filename = "detected_doors.txt"
        try:
            with open(filename, "w") as file:
                for door in self.detected_doors_list:
                    file.write(f"{door}\n")
            print(f"Les portes détectées ont été sauvegardées dans '{filename}'.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des portes détectées: {e}")




    