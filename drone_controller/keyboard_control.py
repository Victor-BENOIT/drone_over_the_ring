from pynput import keyboard

class Keyboard:
    def __init__(self, controller):
        self.controller = controller
        self.listener = None

    def on_press(self, key):
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
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop_listening(self):
        if self.listener:
            self.listener.stop()
