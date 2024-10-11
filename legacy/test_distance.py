import pygame
import threading
import time
from djitellopy import Tello
import cv2

# Initialisation du cascade de détection de visage
face_cascade = cv2.CascadeClassifier("C:\\Users\\fleur\\OneDrive - ESEO\\Bureau\\Ecole\\E5\\PI\\Repositery GitHub\\drone_over_the_ring\\detect_profil.xml")

# Paramètres pour la distance
FOCALE = 1.98e-3  # Focale en mètres
TAILLE_PIX = 5.08e-6  # Taille d'un pixel en mètres
HAUTEUR_REELLE_VISAGE = 26e-2  # Hauteur réelle moyenne d'un visage en mètres

# Initialisation du drone
tello = Tello()
tello.connect()
tello.streamon()  # Active le flux vidéo

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((960, 720))  # Taille de la fenêtre Pygame
pygame.display.set_caption("Tello Drone POV")
font = pygame.font.SysFont("Arial", 30)  # Police pour l'affichage de la batterie

# Variable globale pour stocker le niveau de batterie
battery_level = "N/A"

# Dictionnaire pour stocker les distances de chaque visage (identifié par son index)
distances_visages = {}

# Verrou pour gérer les accès concurrents à distances_visages
lock = threading.Lock()

# Fonction pour calculer la moyenne des distances pour chaque visage toutes les 2 secondes
def calculate_average_distances():
    global distances_visages
    while True:
        time.sleep(2)  # Calculer la moyenne toutes les 2 secondes
        with lock:
            for visage_id in distances_visages:
                if distances_visages[visage_id]:
                    # Calculer la moyenne des distances pour chaque visage
                    moyenne_distance = sum(distances_visages[visage_id]) / len(distances_visages[visage_id])
                    distances_visages[visage_id] = [moyenne_distance]  # Stocker uniquement la moyenne

# Fonction pour afficher la vidéo, détecter les visages et le niveau de batterie dans la fenêtre Pygame
def update_frame():
    global distances_visages

    try:
        frame = tello.get_frame_read().frame  # Lecture de la frame du drone
        if frame is None:
            print("Erreur : Impossible de récupérer le flux vidéo.")
            return

        # Appliquer un flip gauche-droite (miroir horizontal)
        frame = cv2.flip(frame, 1)  # 1 signifie flip horizontal

        # Détection des visages
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)

        # Ajouter les nouvelles distances des visages détectés
        with lock:
            # Ajouter ou mettre à jour les distances de chaque visage détecté
            for i, (x, y, w, h) in enumerate(faces):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Calcul du grandissement à partir de la hauteur du visage détecté
                hauteur_image_pix = h  # Hauteur en pixels du visage dans l'image
                hauteur_image_m = hauteur_image_pix * TAILLE_PIX  # Conversion en mètres
                grandissement = hauteur_image_m / HAUTEUR_REELLE_VISAGE

                # Calcul de la distance entre la caméra et le visage
                distance = FOCALE * (1 / grandissement + 2 + grandissement)  # Formule du grandissement
                distance_cm_temp = int(distance * 100)  # Conversion en centimètres

                # Ajouter la distance à la liste associée au visage dans le dictionnaire
                if i not in distances_visages:
                    distances_visages[i] = []
                distances_visages[i].append(distance_cm_temp)

        # Rotation et affichage sur Pygame
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)  # Conversion en surface Pygame
        screen.blit(frame, (0, 0))  # Affiche la frame sur la fenêtre Pygame

        # Affichage du niveau de batterie en haut à droite
        pygame.draw.rect(screen, (0, 0, 0), (795, 15, 155, 50))
        battery_text = font.render(f"Batterie: {battery_level}%", True, (255, 255, 255))
        screen.blit(battery_text, (800, 20))  # Position en haut à droite

        # Affichage des moyennes des distances des visages détectés
        with lock:
            for i, distances in distances_visages.items():
                if distances:
                    distance_moyenne = distances[0]  # La moyenne est déjà calculée toutes les 2 secondes
                    pygame.draw.rect(screen, (0, 0, 0), (20, 15 + i * 65, 220, 50))
                    visage_text = font.render(f"Visage {i + 1}: {distance_moyenne:.2f}cm", True, (255, 255, 255))
                    screen.blit(visage_text, (25, 20 + i * 65))

        pygame.display.update()

    except Exception as e:
        print(f"Erreur lors de la capture vidéo: {e}")

# Fonction pour mettre à jour le niveau de batterie toutes les 10 secondes
def update_battery():
    global battery_level
    while True:
        try:
            battery_level = tello.get_battery()  # Récupère le niveau de batterie
        except Exception as e:
            print(f"Erreur lors de la récupération de la batterie: {e}")
        time.sleep(10)  # Attendre 10 secondes avant de rafraîchir

# Lancement du contrôle du drone
def start_drone_control():
    print("Lancement du contrôle du drone et de l'affichage vidéo.")

    # Démarrage du thread de mise à jour de la batterie
    battery_thread = threading.Thread(target=update_battery, daemon=True)
    battery_thread.start()

    # Démarrage du thread pour calculer la moyenne des distances
    average_thread = threading.Thread(target=calculate_average_distances, daemon=True)
    average_thread.start()

    # Boucle principale pour l'affichage Pygame
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Fermer la fenêtre Pygame
                running = False
        update_frame()  # Met à jour l'affichage vidéo et batterie

if __name__ == "__main__":
    try:
        start_drone_control()
    finally:
        tello.streamoff()  # Désactive le flux vidéo
        pygame.quit()  # Quitte Pygame proprement
