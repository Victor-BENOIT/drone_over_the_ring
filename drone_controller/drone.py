import cv2
from utils.logging import Logging
from djitellopy import Tello
from drone_controller.movement import Movement
from drone_controller.vision import Vision
from drone_controller.targeting import Target
from drone_controller.flying_modes import IdleMode, ManualMode, AutonomousMode, ScanMode
from config.settings import DRONE_SPEED, MANUAL_MODE, AUTONOMOUS_MODE, SCAN_MODE, IDLE_MODE

class DroneController:
    """
    Classe principale pour le contrôle du drone Tello, gérant les modes de vol, la vision, 
    les mouvements, et les actions de base comme décoller et atterrir.
    
    Attributes:
        tello: L'objet Tello représentant le drone.
        vision: L'objet Vision pour la détection d'objets.
        logging: L'outil de logging.
        movement: L'objet Movement pour les déplacements du drone.
        target: L'objet Target pour le suivi des cibles.
        mode: Le mode de vol actuel du drone (Idle, Manuel, Autonome ou Scan).
    """

    def __init__(self):
        """
        Initialise la classe DroneController, établit la connexion avec le drone, configure la vitesse, et 
        démarre le flux vidéo.
        Le mode de vol est sélectionné en fonction des paramètres de configuration.
        """
        self.tello = Tello()
        self.tello.connect()
        self.tello.set_speed(DRONE_SPEED)
        self.tello.streamon()

        self.vision = Vision()
        self.logging = Logging()
        self.movement = Movement(self)
        self.target = Target()
        
        # Sélection du mode de vol en fonction des paramètres
        if IDLE_MODE:
            self.mode = IdleMode(self)
        elif AUTONOMOUS_MODE:
            self.mode = AutonomousMode(self)
        elif MANUAL_MODE:
            self.mode = ManualMode(self)
        elif SCAN_MODE: 
            self.mode = ScanMode(self)
    
    def takeoff(self):
        """Décolle le drone."""
        self.tello.takeoff()
    
    def land(self):
        """Atterrit le drone."""
        self.tello.land()
    
    def is_flying(self):
        """
        Vérifie si le drone est actuellement en vol.

        Returns:
            bool: True si le drone est en vol, sinon False.
        """
        return self.tello.is_flying

    def stop_video_stream(self):
        """Arrête le flux vidéo en direct du drone."""
        self.tello.streamoff()
        
    def get_frame(self):
        """
        Capture une image du flux vidéo en direct du drone, la retourne horizontalement pour correspondre à la 
        vue utilisateur.
        
        Returns:
            frame: L'image capturée et retournée horizontalement.
        """
        frame = self.tello.get_frame_read().frame
        frame = cv2.flip(frame, 1)
        return frame
