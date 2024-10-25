import cv2
from djitellopy import Tello
from drone_controller.movement import Movement
from drone_controller.vision import Vision
from drone_controller.targeting import Target
from drone_controller.flying_modes import ManualMode, AutonomousMode 
from utils.logging import Logging
from config.settings import DRONE_SPEED, MANUAL_MODE, AUTONOMOUS_MODE

class DroneController:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.set_speed(DRONE_SPEED)
        self.tello.streamon()

        self.vision = Vision()
        self.logging = Logging()
        self.movement = Movement(self)
        self.target = Target()
        if AUTONOMOUS_MODE:
            self.mode = AutonomousMode(self)
        elif MANUAL_MODE:
            self.mode = ManualMode(self)
    
    def takeoff(self):
        self.tello.takeoff()
    
    def land(self):
        self.tello.land()
    
    def is_flying(self):
        return self.tello.is_flying

    def stop_video_stream(self):
        self.tello.streamoff()
        
    def get_frame(self):
        frame = self.tello.get_frame_read().frame
        frame = cv2.flip(frame, 1)
        return frame

