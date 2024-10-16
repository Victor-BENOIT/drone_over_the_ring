#############################################################################################
#                         Paramètres de chemin d'accès
#############################################################################################
CHEMIN_DETECT = "resources/detect_profil.xml"  # Chemin d'accès au fichier de détection de visage


#############################################################################################
#                         Paramètres pour le calcul de distance
#############################################################################################
FOCALE = 1.98e-3  # Focale en mètres
TAILLE_PIX = 5.08e-6  # Taille d'un pixel en mètres
HAUTEUR_REELLE_VISAGE = 26e-2  # Hauteur réelle moyenne d'un visage en mètres


#############################################################################################
#                         Paramètres de déplacement
#############################################################################################
DRONE_SPEED = 100  # 10-100cm
DRONE_DIST = 50  # 20-500cm
MANUAL_MODE = False
AUTONOMOUS_MODE = not MANUAL_MODE


#############################################################################################
#                         Paramètres d'affichage
#############################################################################################
SCREEN_WIDTH = 960 #px
SCREEN_HEIGHT = 720 #px
SCREEN_TITLE = "Tello Drone POV"

#############################################################################################
#                         Paramètres pour le targeting
#############################################################################################
WINDOW_COEF = 0.1 # 0-1

WINDOW_OFFSET_X =  0
WINDOW_OFFSET_Y = -200

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