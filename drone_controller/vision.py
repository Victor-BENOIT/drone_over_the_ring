import cv2
from ultralytics import YOLO
import logging
import pygame
from config.settings import CHEMIN_DETECT, MODEL_HOOP_PATH, THRESHOLD_HOOP, HAUTEUR_REELLE_HOOP, FOCALE, TAILLE_PIX, HAUTEUR_REELLE_VISAGE

class Vision:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(CHEMIN_DETECT)
        self.distance = None
        self.modele_hoop =  YOLO(MODEL_HOOP_PATH, verbose=False) 
        logging.getLogger('ultralytics').setLevel(logging.ERROR) #Ne plus afficher les messages du modèle dans la console

    def process_frame(self, frame, screen):
        # faces = self.get_faces_coordinates(frame)
        # self.update_distance(faces)

        # for (x, y, w, h) in faces:
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        hoops = self.get_hoops(frame)
        self.update_distance(hoops)

        for hoop in hoops:
            x1, y1, w, h, score = hoop
            cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 4)
            cv2.putText(frame, f"HOOP {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 0, 0), 3, cv2.LINE_AA)
            #print(f"Coordonnées : {x1}, {y1}, {w}, {h}")

        # Rotation and Pygame display
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))

    def get_faces_coordinates(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    

    def update_distance(self, list):
        if len(list) == 1:
            for (x, y, w, h, _) in list:
            # Calcul du grandissement
                grandissement = h * TAILLE_PIX
            
            # Utilisation de la formule simplifiée
                self.distance = int((HAUTEUR_REELLE_HOOP * FOCALE) / grandissement * 100)
        elif len(list) == 0:
            self.distance = None


    def get_hoops(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hoop = self.modele_hoop(frame_rgb)[0]
        hoops = []

        for result in results_hoop.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            w = x2 - x1
            h = y2 - y1
            x1 = int(x1)
            y1 = int(y1)
            w = int(w)
            h = int(h)
            if score > THRESHOLD_HOOP:
                hoops.append([x1, y1, w, h, score])
        return hoops