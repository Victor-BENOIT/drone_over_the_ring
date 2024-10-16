import cv2
import pygame
from config.settings import CHEMIN_DETECT

class Vision:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(CHEMIN_DETECT)

    def process_frame(self, frame, screen):
        faces = self.get_faces_coordinates(frame)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Rotation and Pygame display
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))

    def get_faces_coordinates(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)