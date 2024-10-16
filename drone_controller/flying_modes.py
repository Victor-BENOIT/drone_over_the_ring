from drone_controller.keyboard_control import Keyboard

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
        print(self.vision.distance)
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

    def start(self):
        print("Mode autonome activé.\nTracking du visage activé")
        if not self.controller.is_flying():
            self.controller.takeoff()
        while self.tello.get_height() < 150:
            self.controller.movement.move_up()

    def main_loop(self):
        self.horizontal_vertical_tracking() #Execute une instance de horizontal_vertical_tracking
        self.distance_tracking()

    def stop(self):
        if self.controller.is_flying():
            self.controller.land()

    def horizontal_vertical_tracking(self):
        faces = self.vision.get_faces_coordinates(self.controller.get_frame())
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            # print(x, y, w, h)
            x_center_box = x + w / 2
            y_center_box = y + h / 2

            x_corner, y_corner, w_width, w_height = self.controller.target.get_target_window()

            min_x_window = x_corner
            max_x_window = x_corner + w_width
            min_y_window = y_corner
            max_y_window = y_corner + w_height

            # Vérifier les conditions et ajuster la position du drone
            if y_center_box < min_y_window:  # Le visage est en dessous de la fenêtre
                self.controller.movement.move_up()
            elif y_center_box > max_y_window:  # Le visage est au-dessus de la fenêtre
                self.controller.movement.move_down()

            if x_center_box < min_x_window:  # Le visage est à gauche de la fenêtre
                self.controller.movement.move_right()
            elif x_center_box > max_x_window:  # Le visage est à droite de la fenêtre
                self.controller.movement.move_left()

    
    def distance_tracking(self):
        distance = self.vision.distance
        if distance is None:
            return
        if distance > 100:
            self.controller.movement.move_forward()
        elif distance < 50:
            self.controller.movement.move_backward()
