#################################################################################################################
#                                       Paramètres de chemin d'accès
#################################################################################################################
CHEMIN_DETECT = "resources/detect_profil.xml"  # Chemin d'accès au fichier de détection de visage
MODEL_HOOP_HEX_PATH = r'resources\runs\detect\train9\weights\last.pt'


#################################################################################################################
#                                       Paramètres pour le calcul de distance
#################################################################################################################
FOCALE = 1.98e-3  # Focale de la caméra en mètres
TAILLE_PIX = 5.08e-6  # Taille d'un pixel en mètres
HAUTEUR_REELLE_VISAGE = 26e-2  # Hauteur réelle d'un visage en mètres
HAUTEUR_REELLE_HOOP = 0.62 * 2 # Hauteur réelle d'un cercle en mètres // RAPPORT DE CORRECTION DE 2 ARBITRAIRE


#################################################################################################################
#                                       Paramètres pour le modele de détection
#################################################################################################################
THRESHOLD_HOOP = 0.9 # Seuil de detection cercle

#################################################################################################################
#                                       Paramètres de logging (stockage des deplacements du drone)
#################################################################################################################
LOGGING_ENABLED = True


#################################################################################################################
#                                       Paramètres de déplacement
#################################################################################################################
DRONE_SPEED = 100  # 10-100 (vitesse de déplacement par défaut)
DRONE_DIST = 20  # 20-500cm (distance de déplacement par défaut)
MANUAL_MODE = False # True pour le mode manuel, False pour le mode autonome
AUTONOMOUS_MODE = not MANUAL_MODE 


#################################################################################################################
#                                       Paramètres d'affichage
#################################################################################################################
SCREEN_WIDTH = 960 #Largeur de l'écran en px
SCREEN_HEIGHT = 720 #Hauteur de l'écran en px
SCREEN_TITLE = "Tello Drone POV" #Titre de la fenêtre d'affichage

BATTERY_DISPLAY_X = 795 # Position x du coin haut droit de la batterie
BATTERY_DISPLAY_Y = 15 # Position y du coin haut droit de la batterie
BATTERY_DISPLAY_WIDTH = 155 # Largeur de la zone d'affichage de la batterie
BATTERY_DISPLAY_HEIGHT = 50 # Hauteur de la zone d'affichage de la batterie

DIST_DISPLAY_X = 15 # Position x du coin haut gauche de la distance
DIST_DISPLAY_Y = 15 # Position y du coin haut gauche de la distance
DIST_DISPLAY_WIDTH = 190 # Largeur de la zone d'affichage de la distance
DIST_DISPLAY_HEIGHT = 50 # Hauteur de la zone d'affichage de la distance

#################################################################################################################
#                                       Paramètres pour le targeting
#################################################################################################################
WINDOW_COEF = 0.25 # Coefficient de la taille de la zone target (par rapport à la taille de l'écran)

WINDOW_OFFSET_X = 0 # Offset en x de la zone target
WINDOW_OFFSET_Y = -200 # Offset en y de la zone target -100 pour aller plus bas / 100 pour aller plus haut

square_target = True
# Largeur et Hauteur de la zone target
WINDOW_HEIGHT = SCREEN_HEIGHT * WINDOW_COEF #px
if square_target:
    WINDOW_WIDTH = WINDOW_HEIGHT #px
else :
    WINDOW_WIDTH = SCREEN_WIDTH * WINDOW_COEF #px

# Coordonnées pour le coin haut droit de la zone target
WINDOW_CORNER_X = SCREEN_WIDTH / 2 - WINDOW_WIDTH /2 + WINDOW_OFFSET_X #px
WINDOW_CORNER_Y = SCREEN_HEIGHT / 2 - WINDOW_HEIGHT / 2 + WINDOW_OFFSET_Y #px

TARGET_DIST = 125 # Distance fisée par rapport à la cible en cm
MOVE_RATIO = 0.6 # [0:1] Ratio de déplacement par rapport à la distance de la cible
DEAD_ZONE = 10 # Zone morte pour le déplacement en cm