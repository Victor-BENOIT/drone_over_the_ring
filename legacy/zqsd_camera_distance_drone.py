from djitellopy import Tello
from pynput import keyboard
import pygame
import cv2
import threading
import time

# Initialisation du cascade de détection de visage
face_cascade = cv2.CascadeClassifier("drone_over_the_ring/legacy/detect_profil.xml")

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

# Fonction pour afficher la vidéo, détecter les visages et le niveau de batterie dans la fenêtre Pygame
def update_frame():
    try:
        frame = tello.get_frame_read().frame  # Lecture de la frame du drone
        if frame is None:
            print("Erreur : Impossible de récupérer le flux vidéo.")
            return

        tickmark = cv2.getTickCount()  # Pour mesurer les FPS

        # Détection des visages
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)

        # Dessiner des rectangles autour des visages détectés
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Calcul des FPS
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - tickmark)
        cv2.putText(frame, "FPS: {:05.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Rotation et affichage sur Pygame
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)  # Conversion en surface Pygame
        screen.blit(frame, (0, 0))  # Affiche la frame sur la fenêtre Pygame

        # Affichage du niveau de batterie en haut à droite
        pygame.draw.rect(screen, (0, 0, 0), (795, 15, 155, 50))
        battery_text = font.render(f"Batterie: {battery_level}%", True, (255, 255, 255))
        screen.blit(battery_text, (800, 20))  # Position en haut à droite

        pygame.display.update()  # Met à jour l'affichage
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
            update_frame()  # Met à jour l'affichage vidéo et batterie
        listener.stop()

if __name__ == "__main__":
    try:
        start_drone_control()
    finally:
        tello.streamoff()  # Désactive le flux vidéo
        pygame.quit()  # Quitte Pygame proprement
