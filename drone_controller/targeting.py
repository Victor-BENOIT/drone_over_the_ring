from config.settings import WINDOW_CORNER_X, WINDOW_CORNER_Y, WINDOW_WIDTH, WINDOW_HEIGHT

class Target:
    """
    Classe pour représenter la cible dans une fenêtre avec des dimensions et une position spécifiques.
    """

    def __init__(self):
        """
        Initialise la classe Target.
        """
        return
    
    def get_target_window(self):
        """
        Récupère les coordonnées et dimensions de la fenêtre cible.

        Returns:
            tuple: Coordonnées (x, y) du coin supérieur gauche, largeur et hauteur de la fenêtre cible.
        """
        return (WINDOW_CORNER_X, WINDOW_CORNER_Y, WINDOW_WIDTH, WINDOW_HEIGHT)
