import cv2
from ultralytics import YOLO
import pygame
from config.settings import CHEMIN_DETECT, MODEL_HOOP_PATH, THRESHOLD_HOOP
from config.settings import FOCALE, TAILLE_PIX, HAUTEUR_REELLE_VISAGE

class Vision:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(CHEMIN_DETECT)
        self.distance = None
        self.modele_hoop =  YOLO(MODEL_HOOP_PATH)

    def process_frame(self, frame, screen):
        faces = self.get_faces_coordinates(frame)
        self.update_distance(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Rotation and Pygame display
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))

    def get_faces_coordinates(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    

    def update_distance(self, faces):
        if(len(faces) == 1):
            for (x, y, w, h) in faces:
                grandissement = h * TAILLE_PIX / HAUTEUR_REELLE_VISAGE
                self.distance = int(FOCALE * (1 / grandissement + 2 + grandissement) * 100)
        elif len(faces) == 0:
           self.distance = None


    def get_hoops(self, frame):
        return