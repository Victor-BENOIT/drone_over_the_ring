from drone_controller.keyboard_control import Keyboard
from config.settings import TARGET_DIST, DEAD_ZONE, MOVE_RATIO

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

    def start(self):
        print("Mode autonome activé.\nTracking du visage activé")
        if not self.controller.is_flying():
            self.controller.takeoff()
        while self.tello.get_height() < 120:
            self.controller.movement.move_up(50)

    def main_loop(self):
        # print("LOCK: " + str(self.locked_horizontal) + " " + str(self.locked_vertical) + " " + str(self.locked_distance))

        if self.locked_horizontal == True & self.locked_vertical == True & self.locked_distance == True:
            self.controller.logging.add_gate_marker("hoop")
            self.controller.movement.move_forward(int(self.vision.distance) + 170)
            self.controller.land()
        else :
            self.horizontal_vertical_tracking()
            self.distance_tracking()

    def stop(self):
        if self.controller.is_flying():
            self.controller.land()

    def horizontal_vertical_tracking(self):
        list = self.vision.get_hoops(self.controller.get_frame())
        if len(list) == 1:
            (x, y, w, h, _) = list[0]
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
