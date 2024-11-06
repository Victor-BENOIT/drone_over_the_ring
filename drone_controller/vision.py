import cv2
from ultralytics import YOLO
import logging
from config.settings import CHEMIN_DETECT, MODEL_HOOP_PATH, MODEL_HEX_PATH, THRESHOLD_HEX, THRESHOLD_HOOP, HAUTEUR_REELLE_HOOP, FOCALE, TAILLE_PIX, HAUTEUR_REELLE_VISAGE

class Vision:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(CHEMIN_DETECT)
        self.distance = None
        self.model_hoop = YOLO(MODEL_HOOP_PATH, verbose=False)
        self.model_hex = YOLO(MODEL_HEX_PATH, verbose=False) 
        self.gates = []
        logging.getLogger('ultralytics').setLevel(logging.ERROR) #Ne plus afficher les messages du modèle dans la console

    def process_frame(self, frame):
        self.gates = self.get_gates(frame)
        self.update_distance(self.gates)

    def get_faces_coordinates(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    

    def update_distance(self, list):
        if(len(list) == 1):
            for (_, _, _, h, _, _) in list:
                grandissement = h * TAILLE_PIX / HAUTEUR_REELLE_HOOP
                self.distance = int(FOCALE * (1 / grandissement + 2 + grandissement) * 100)
        elif len(list) == 0:
           self.distance = None


    def get_gates(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hoops = self.model_hoop(frame_rgb)[0]
        results_hex = self.model_hex(frame_rgb)[0]
        gates = []

        for result in results_hoops.boxes.data.tolist():
            x1, y1, x2, y2, score, _ = result
            w = x2 - x1
            h = y2 - y1
            x1 = int(x1)
            y1 = int(y1)
            w = int(w)
            h = int(h)
            if score > THRESHOLD_HOOP:
                gates.append([x1, y1, w, h, score, "hoop"])

        for result in results_hex.boxes.data.tolist():
            x1, y1, x2, y2, score, _ = result
            w = x2 - x1
            h = y2 - y1
            x1 = int(x1)
            y1 = int(y1)
            w = int(w)
            h = int(h)
            if score > THRESHOLD_HEX:
                gates.append([x1, y1, w, h, score, "hex"])
                
        return gates