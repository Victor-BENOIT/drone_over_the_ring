from pynput import keyboard

class Keyboard:
    """
    Classe pour gérer les entrées clavier et exécuter les actions de contrôle du drone.

    Attributes:
        controller: L'objet contrôleur pour gérer les actions du drone.
        listener: Un écouteur de clavier pour détecter les appuis de touche.
    """

    def __init__(self, controller):
        """
        Initialise la classe Keyboard avec un contrôleur.

        Args:
            controller: L'objet contrôleur contenant les actions de mouvement et de vol du drone.
        """
        self.controller = controller
        self.listener = None

    def on_press(self, key):
        """
        Déclenche les actions correspondantes selon la touche appuyée.

        Args:
            key: La touche appuyée détectée par l'écouteur.
        """
        try:
            if key.char == 'z':
                self.controller.movement.move_forward()
            elif key.char == 'q':
                self.controller.movement.move_left()
            elif key.char == 's':
                self.controller.movement.move_backward()
            elif key.char == 'd':
                self.controller.movement.move_right()
            elif key.char == 'a':
                self.controller.movement.move_up()
            elif key.char == 'e':
                self.controller.movement.move_down()
            elif key.char == 'o':
                if not self.controller.is_flying():
                    self.controller.takeoff()
                else:
                    self.controller.land()
        except AttributeError:
            pass  # Ignore other keys

    def start_listening(self):
        """
        Démarre l'écoute des entrées clavier.
        """
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop_listening(self):
        """
        Arrête l'écoute des entrées clavier si elle est en cours.
        """
        if self.listener:
            self.listener.stop()
