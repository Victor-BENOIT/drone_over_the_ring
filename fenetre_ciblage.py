import cv2
import pygame
import threading
import time
from djitellopy import Tello
from pynput import keyboard

# Initialisation du cascade de détection de visage
face_cascade = cv2.CascadeClassifier("C:\\Users\\user\\Desktop\\user\\e5e\\pi\\Repositery GitHub\\drone_over_the_ring\\detect_profil.xml")


# Paramètres pour la distance
FOCALE = 1.98e-3  # Focale en mètres
TAILLE_PIX = 5.08e-6  # Taille d'un pixel en mètres
HAUTEUR_REELLE_VISAGE = 26e-2  # Hauteur réelle moyenne d'un visage en mètres

DRONE_SPEED = 100  # 10-100
DRONE_DIST = 20  # 20-500

# Taille Ecran Pygame
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720

# Fenetre de ciblage
WINDOW_COEF = 0.1 # 0-1
#WINDOW_WIDTH = SCREEN_WIDTH * WINDOW_COEF
WINDOW_HEIGHT = SCREEN_HEIGHT * WINDOW_COEF
WINDOW_WIDTH = WINDOW_HEIGHT
WINDOW_CORNER_X = SCREEN_WIDTH / 2 - WINDOW_WIDTH /2
WINDOW_CORNER_Y = SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2



# Initialisation du drone
tello = Tello()
tello.connect()
tello.streamon()  # Active le flux vidéo
tello.set_speed(DRONE_SPEED)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Taille de la fenêtre Pygame
pygame.display.set_caption("Tello Drone POV")
font = pygame.font.SysFont("Arial", 30)  # Police pour l'affichage de la batterie

# Variable globale pour stocker le niveau de batterie
battery_level = "N/A"

# Fonction pour contrôler le drone avec le clavier
def on_press(key):
    try:
        if key.char == 'z':  # Avancer
            tello.move_forward(DRONE_DIST)
        elif key.char == 'q':  # Gauche
            tello.move_left(DRONE_DIST)
        elif key.char == 's':  # Reculer
            tello.move_back(DRONE_DIST)
        elif key.char == 'd':  # Droite
            tello.move_right(DRONE_DIST)
        elif key.char == 'a':  # S'élever
            tello.move_up(DRONE_DIST)
        elif key.char == 'e':  # Descendre
            tello.move_down(DRONE_DIST)
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

        # Appliquer un flip gauche-droite (miroir horizontal)
        frame = cv2.flip(frame, 1)  # 1 signifie flip horizontal

        # Détection des visages
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)

        # Dessiner des rectangles autour des visages détectés et calculer la distance
        face_count = len(faces)  # Compte le nombre de visages détectés

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if face_count == 1:
            (x, y, w, h) = faces[0]
            x_center_box = x + w / 2
            y_center_box = y + h / 2

            # Récupérer les coordonnées de la fenêtre de ciblage
            min_x_window = WINDOW_CORNER_X
            max_x_window = WINDOW_CORNER_X + WINDOW_WIDTH
            min_y_window = WINDOW_CORNER_Y
            max_y_window = WINDOW_CORNER_Y + WINDOW_HEIGHT

                # Vérifier les conditions et ajuster la position du drone
            if y_center_box < min_y_window:  # Le visage est en dessous de la fenêtre
                tello.move_up(DRONE_DIST)  # Le drone monte
            elif y_center_box > max_y_window:  # Le visage est au-dessus de la fenêtre
                tello.move_down(DRONE_DIST)  # Le drone descend

            if x_center_box < min_x_window:  # Le visage est à gauche de la fenêtre
                tello.move_right(DRONE_DIST)  # Le drone se décale à droite
            elif x_center_box > max_x_window:  # Le visage est à droite de la fenêtre
                tello.move_left(DRONE_DIST)  # Le drone se décale à gauche


        # Rotation et affichage sur Pygame
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = pygame.surfarray.make_surface(frame)  # Conversion en surface Pygame
        screen.blit(frame, (0, 0))  # Affiche la frame sur la fenêtre Pygame


        # Affichage de la fenetre de ciblage
        pygame.draw.rect(screen, (255, 0, 0), (WINDOW_CORNER_X, WINDOW_CORNER_Y, WINDOW_WIDTH, WINDOW_HEIGHT), 5)

        # Affichage du niveau de batterie en haut à droite
        pygame.draw.rect(screen, (0, 0, 0), (795, 15, 155, 50))
        battery_text = font.render(f"Batterie: {battery_level}%", True, (255, 255, 255))
        screen.blit(battery_text, (800, 20))  # Position en haut à droite

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
