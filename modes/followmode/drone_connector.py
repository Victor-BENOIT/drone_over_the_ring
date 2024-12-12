from djitellopy import Tello

class DroneConnector:
    def __init__(self):
        self.drone = None
        self.connected = False

    def connect(self):
        """Connecte le drone."""
        self.drone = Tello()
        try:
            self.drone.connect()
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to the drone: {e}")
            self.connected = False

    def takeoff(self):
        """Fait décoller le drone."""
        self.drone.takeoff()

    def land(self):
        """Fait atterrir le drone."""
        self.drone.land()

    def disconnect(self):
        """Déconnecte le drone."""
        self.drone.disconnect()
        self.connected = False