import cv2
from ultralytics import YOLO
import logging
from config.settings import CHEMIN_DETECT, MODEL_HOOP_PATH, MODEL_HEX_PATH, THRESHOLD_HEX, THRESHOLD_HOOP, HAUTEUR_REELLE_HOOP, FOCALE, TAILLE_PIX, HAUTEUR_REELLE_HEX_VERTICAL, HAUTEUR_REELLE_HEX_HORIZONTAL

class Vision:
    """
    Classe pour la détection et l'évaluation de distance des objets (cerceau et hexagone) dans les images.

    Attributes:
        face_cascade (cv2.CascadeClassifier): Classificateur en cascade pour la détection de visages.
        distance (float or None): La distance calculée de l'objet détecté (cerceau ou hexagone).
        model_hoop (YOLO): Modèle YOLO pour la détection de cerceaux.
        model_hex (YOLO): Modèle YOLO pour la détection d'hexagones.
        gates (list): Liste des objets détectés sous forme de coordonnées et de classe.
    """

    def __init__(self):
        """
        Initialise la classe Vision avec les modèles et les paramètres de détection.
        """
        self.face_cascade = cv2.CascadeClassifier(CHEMIN_DETECT)
        self.distance = None
        self.model_hoop = YOLO(MODEL_HOOP_PATH, verbose=False)
        self.model_hex = YOLO(MODEL_HEX_PATH, verbose=False)
        self.gates = []
        logging.getLogger('ultralytics').setLevel(logging.ERROR) # Ne plus afficher les messages du modèle dans la console

    def process_frame(self, frame):
        """
        Traite une image pour détecter les objets et mettre à jour la distance de l'objet le plus proche.

        Args:
            frame (np.ndarray): Image d'entrée à traiter.
        """
        self.gates = self.get_gates(frame)
        self.update_distance(self.gates)

    def get_faces_coordinates(self, frame):
        """
        Détecte les coordonnées des visages dans l'image.

        Args:
            frame (np.ndarray): Image d'entrée pour la détection de visages.

        Returns:
            list: Liste de rectangles englobants (x, y, w, h) des visages détectés.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    
    def update_distance(self, list):
        """
        Met à jour la distance à l'objet détecté en fonction de sa taille et de sa classe (cerceau ou hexagone).

        Args:
            list (list): Liste des objets détectés avec leurs dimensions et classes.
        """
        if len(list) == 1:
            for (_, _, w, h, _, class_id) in list:

                if class_id == "hoop":
                    grandissement_vertical = h * TAILLE_PIX / HAUTEUR_REELLE_HOOP
                    grandissement_horizontal = w * TAILLE_PIX / HAUTEUR_REELLE_HOOP
                    dist_vertical = int(FOCALE * (1 / grandissement_vertical + 2 + grandissement_vertical) * 100)
                    dist_horizontal = int(FOCALE * (1 / grandissement_horizontal + 2 + grandissement_horizontal) * 100)
                    self.distance = dist_vertical if dist_vertical < dist_horizontal else dist_horizontal

                elif class_id == "hex":
                    grandissement_vertical = h * TAILLE_PIX / HAUTEUR_REELLE_HEX_VERTICAL
                    grandissement_horizontal = w * TAILLE_PIX / HAUTEUR_REELLE_HEX_HORIZONTAL
                    dist_vertical = int(FOCALE * (1 / grandissement_vertical + 2 + grandissement_vertical) * 100)
                    dist_horizontal = int(FOCALE * (1 / grandissement_horizontal + 2 + grandissement_horizontal) * 100)
                    self.distance = dist_vertical if dist_vertical < dist_horizontal else dist_horizontal
                    
        elif len(list) == 0:
           self.distance = None

    def get_gates(self, frame):
        """
        Détecte les objets dans l'image en utilisant les modèles YOLO pour les cerceaux et hexagones.

        Args:
            frame (np.ndarray): Image d'entrée pour la détection.

        Returns:
            list: Liste des objets détectés avec leurs coordonnées, dimensions, score de confiance et classe.
        """
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
                gates.append([x1, y1, w, h, round(score, 2), "hoop"])

        for result in results_hex.boxes.data.tolist():
            x1, y1, x2, y2, score, _ = result
            w = x2 - x1
            h = y2 - y1
            x1 = int(x1)
            y1 = int(y1)
            w = int(w)
            h = int(h)
            if score > THRESHOLD_HEX:
                gates.append([x1, y1, w, h, round(score, 2), "hex"])

        return gates
