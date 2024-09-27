from djitellopy import Tello
from pynput import keyboard
import pygame
import cv2
import numpy as np
import threading
import time

DRONE_SPEED = 100  # 10-100
DRONE_MOVE = 20  # 20-500

# Initialisation du drone
tello = Tello()
tello.connect()
tello.streamon()  # Active le flux vidéo

tello.set_speed(DRONE_SPEED)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((960, 720))  # Taille de la fenêtre Pygame
pygame.display.set_caption("Tello Drone POV")
font = pygame.font.SysFont("Arial", 30)  # Police pour l'affichage de la batterie

# Variable globale pour stocker le niveau de batterie
battery_level = "N/A"

# Fonction pour calculer la distance des objets détectés
def calculer_distance(diameters, focale=1.75e-3, taille_pix=1.56e-6, diametre_objet_m=7.3e-2):
    diametre_image_m = diameters * taille_pix
    grandissement = diametre_image_m / diametre_objet_m
    distance = focale * (1/grandissement + 2 + grandissement)
    return distance * 100  # en cm

# Fonction pour contrôler le drone avec le clavier
def on_press(key):
    try:
        if key.char == 'z':  # Avancer
            tello.move_forward(DRONE_MOVE)
        elif key.char == 'q':  # Gauche
            tello.move_left(DRONE_MOVE)
        elif key.char == 's':  # Reculer
            tello.move_back(DRONE_MOVE)
        elif key.char == 'd':  # Droite
            tello.move_right(DRONE_MOVE)
        elif key.char == 'a':  # S'élever
            tello.move_up(DRONE_MOVE)
        elif key.char == 'e':  # Descendre
            tello.move_down(DRONE_MOVE)
        elif key.char == 'o':  # Décollage ou atterrissage
            if not tello.is_flying:
                tello.takeoff()
            else:
                tello.land()
    except AttributeError:
        pass  # Ignore les autres touches

def update_frame():
    frame = tello.get_frame_read().frame  # Lecture de la frame du drone
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotation de 90 degrés vers la droite
    
    # Traitement de l'image (conversion en niveaux de gris, binarisation adaptative)
    image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    image_bin = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Filtrage morphologique (avec des éléments structurants plus grands)
    elem_struct1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))  # Plus grand élément structurant
    elem_struct2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # Plus grand élément structurant
    image_dilat = cv2.dilate(image_bin, elem_struct1)
    image_filtered = cv2.erode(image_dilat, elem_struct2)

    # Labelisation et détection des objets
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image_filtered, connectivity=8)

    # Dessiner les objets détectés et calculer les distances
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        if area > 200:  # Augmenter le seuil pour filtrer les petits objets
            diameters = np.mean([w, h])  # Approximation du diamètre
            distance_cm = calculer_distance(diameters)

            # Dessiner des cercles autour des objets détectés
            center = (int(centroids[i][0]), int(centroids[i][1]))
            radius = int(diameters / 2)
            cv2.circle(frame, center, radius, (0, 255, 0), 2)

            # Afficher la distance en cm
            cv2.putText(frame, f'{distance_cm:.1f} cm', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Conversion de la frame en surface Pygame
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))  # Affiche la frame sur la fenêtre Pygame

    # Affichage du niveau de batterie en haut à droite
    pygame.draw.rect(screen, (0, 0, 0), (795, 15, 155, 50))
    battery_text = font.render(f"Batterie: {battery_level}%", True, (255, 255, 255))
    screen.blit(battery_text, (800, 20))  # Position en haut à droite

    pygame.display.update()  # Met à jour l'affichage

# Fonction pour mettre à jour le niveau de batterie toutes les 10 secondes
def update_battery():
    global battery_level
    while True:
        battery_level = tello.get_battery()  # Récupère le niveau de batterie
        time.sleep(10)  # Attendre 10 secondes avant de rafraîchir

# Lancement de l'écouteur de clavier et de l'affichage
def start_drone_control():
    print("Contrôles du drone activés : ZQSD pour déplacement, A pour s'élever, E pour descendre, O pour décollage/atterrissage.")

    # Démarrage du thread de mise à jour de la batterie
    battery_thread = threading.Thread(target=update_battery, daemon=True)
    battery_thread.start()

    # Boucle principale pour l'affichage Pygame et l'écoute du clavier
    with keyboard.Listener(on_press=on_press) as listener:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Fermer la fenêtre Pygame
                    running = False
            update_frame()  # Met à jour l'affichage vidéo, détection et batterie
        listener.stop()

if __name__ == "__main__":
    start_drone_control()
    tello.streamoff()  # Désactive le flux vidéo
    pygame.quit()  # Quitte Pygame proprement
