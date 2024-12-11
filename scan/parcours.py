import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1000
HAUTEUR = 833
BLANC = (255, 255, 255)
BLEU = (0, 0, 255)
ROUGE = (255, 0, 0)
NOIR = (0, 0, 0)
GRIS = (200, 200, 200)
VERT = (0, 255, 0)
ROUGE_ZONE = (255, 0, 0)
RAYON_CERCLE = 10
LONGUEUR_PORTE = 100
RAYON_ZONE = 100
LONGUEUR_TRAVERSEE = 100
MIN_DEPLACEMENT = 33
MAX_DEPLACEMENT = 333
VITESSE_TRAVERSEE = 1
MAX_TENTATIVES = 100
DISTANCE_POST_TRAVERSEE = 1
ANGLE_ROTATION = math.pi / 12  # 15 degrés pour la rotation d'évitement

# Création de la fenêtre
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Traversée des Portes")

class Porte:
    def __init__(self, couleur, x1=None, y1=None, angle=None, portes_existantes=None):
        self.couleur = couleur
        self.traversee = False
        self.active = True

        # Si les coordonnées et l'angle sont fournis, utilisez-les
        if x1 is not None and y1 is not None and angle is not None:
            self.x1 = x1  # Centre de la porte
            self.y1 = y1
            self.centre_x = self.x1  # Alias pour compatibilité
            self.centre_y = self.y1  # Alias pour compatibilité
            self.angle = angle
            
            # Calcul des extrémités en fonction du centre
            demi_longueur = LONGUEUR_PORTE / 2
            self.dx = math.cos(self.angle)
            self.dy = math.sin(self.angle)
            
            # Calcul des extrémités
            self.x2 = self.x1 + demi_longueur * self.dx
            self.y2 = self.y1 + demi_longueur * self.dy
            self.x3 = self.x1 - demi_longueur * self.dx
            self.y3 = self.y1 - demi_longueur * self.dy
            
            # La normale pour les collisions (orthogonale à la direction de la porte)
            self.normal_x = -self.dy
            self.normal_y = self.dx
            
            # Vérification de chevauchement avec d'autres portes
            self.placement_reussi = not self.chevauche_autres_portes(portes_existantes if portes_existantes else [])
        else:
            # Sinon, procédez au placement aléatoire
            self.placement_reussi = self.placer_aleatoirement(portes_existantes if portes_existantes else [])
        
        if self.placement_reussi:
            self.calculer_points_entree_sortie()
        self.points_traverses = set()

    def distance_entre_centres(self, autre_porte):
        dx = self.centre_x - autre_porte.centre_x
        dy = self.centre_y - autre_porte.centre_y
        return math.sqrt(dx * dx + dy * dy)

    def chevauche_autres_portes(self, portes_existantes):
        distance_min = 2 * RAYON_ZONE
        for autre_porte in portes_existantes:
            if self.distance_entre_centres(autre_porte) < distance_min:
                return True
        return False

    def placer_aleatoirement(self, portes_existantes):
        for _ in range(MAX_TENTATIVES):
            self.x1 = random.randint(RAYON_ZONE, LARGEUR - RAYON_ZONE)
            self.y1 = random.randint(RAYON_ZONE, HAUTEUR - RAYON_ZONE)
            self.angle = random.uniform(0, 2 * math.pi)
            
            self.x2 = self.x1 + LONGUEUR_PORTE * math.cos(self.angle)
            self.y2 = self.y1 + LONGUEUR_PORTE * math.sin(self.angle)
            
            self.centre_x = (self.x1 + self.x2) / 2
            self.centre_y = (self.y1 + self.y2) / 2
            
            if (RAYON_ZONE <= self.centre_x <= LARGEUR - RAYON_ZONE and 
                RAYON_ZONE <= self.centre_y <= HAUTEUR - RAYON_ZONE):
                
                self.dx = math.cos(self.angle)
                self.dy = math.sin(self.angle)
                self.normal_x = -self.dy
                self.normal_y = self.dx
                
                if not self.chevauche_autres_portes(portes_existantes):
                    return True
        return False

    def calculer_points_entree_sortie(self):
        self.pointA = (
            self.centre_x + RAYON_ZONE * self.normal_x,
            self.centre_y + RAYON_ZONE * self.normal_y
        )
        self.pointB = (
            self.centre_x - RAYON_ZONE * self.normal_x,
            self.centre_y - RAYON_ZONE * self.normal_y
        )

    def dessiner(self):
        # Choisir la couleur en fonction de l'état d'activation
        couleur_zone = VERT if self.active else ROUGE_ZONE
        transparence = 100  # Augmentation de la transparence pour une meilleure visibilité
        
        # Création d'une surface transparente pour la zone
        surface_transparente = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        pygame.draw.circle(surface_transparente, (*couleur_zone, transparence), 
                        (int(self.centre_x), int(self.centre_y)), RAYON_ZONE)
        ecran.blit(surface_transparente, (0, 0))
        
        # Dessiner la ligne de la porte
        epaisseur = 3 if self.active else 1
        pygame.draw.line(ecran, self.couleur, (self.x2, self.y2), (self.x3, self.y3), epaisseur)
        
        # Dessiner les points A et B
        pygame.draw.circle(ecran, NOIR, (int(self.pointA[0]), int(self.pointA[1])), 5)
        pygame.draw.circle(ecran, NOIR, (int(self.pointB[0]), int(self.pointB[1])), 5)
        
        # Afficher les lettres A et B
        font = pygame.font.Font(None, 24)
        text_a = font.render("A", True, ROUGE)
        text_b = font.render("B", True, ROUGE)
        ecran.blit(text_a, (int(self.pointA[0]) - 8, int(self.pointA[1]) - 12))
        ecran.blit(text_b, (int(self.pointB[0]) - 8, int(self.pointB[1]) - 12))

    def distance_au_point(self, x, y):
        return math.sqrt((x - self.centre_x)**2 + (y - self.centre_y)**2)

class Cercle:
    def __init__(self, portes):
        self.x = 500
        self.y = 33
        self.trace = [(self.x, self.y)]
        self.portes_traversees = 0
        self.en_traversee = False
        self.point_cible = None
        self.porte_actuelle = None
        self.en_mouvement_post_traversee = False
        self.direction_post_traversee = None
        self.direction_traversee = {'dx': 0, 'dy': 0}
        self.en_evitement = False
        self.angle_actuel = 0
        self.segment_distance = 0
        self.point_intermediaire = None
        self.tentatives_rotation = 0
        self.derniere_position = (self.x, self.y)
        self.temps_immobile = 0
        self.distance_totale = 0  # Nouvelle variable pour stocker la distance totale

    def calculer_distance_trace(self):
        """Calcule la distance totale parcourue en suivant la trace"""
        distance = 0
        for i in range(len(self.trace) - 1):
            x1, y1 = self.trace[i]
            x2, y2 = self.trace[i + 1]
            segment = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            distance += segment
        return distance

    def mettre_a_jour_trace(self, nouvelle_position):
        """Met à jour la trace et calcule la nouvelle distance"""
        if self.trace:
            derniere_pos = self.trace[-1]
            nouveau_segment = math.sqrt(
                (nouvelle_position[0] - derniere_pos[0]) ** 2 + 
                (nouvelle_position[1] - derniere_pos[1]) ** 2
            )
            self.distance_totale += nouveau_segment
        self.trace.append(nouvelle_position)

    def contourner_obstacle(self, portes, porte_cible):
        """Effectue un déplacement segmenté pour éviter les obstacles en choisissant le chemin le plus court"""
        # Vérifier si le cercle est bloqué
        distance_derniere_pos = math.sqrt(
            (self.x - self.derniere_position[0])**2 + 
            (self.y - self.derniere_position[1])**2
        )
        
        if distance_derniere_pos < 1:  # Si presque immobile
            self.temps_immobile += 1
        else:
            self.temps_immobile = 0
            
        # Si bloqué trop longtemps, essayer une nouvelle direction
        if self.temps_immobile > 10:
            # Alterner entre rotation horaire et anti-horaire
            if random.random() < 0.5:
                self.angle_actuel += math.pi/3
            else:
                self.angle_actuel -= math.pi/3
            self.temps_immobile = 0
            self.tentatives_rotation += 1
            
        # Si trop de tentatives de rotation, chercher un nouveau point cible
        if self.tentatives_rotation > 6:
            self.trouver_nouveau_point_intermediaire(portes, porte_cible)
            self.tentatives_rotation = 0
            
        if not self.en_evitement or not self.point_intermediaire:
            self.trouver_nouveau_point_intermediaire(portes, porte_cible)
            self.en_evitement = True
            self.segment_distance = 0
            
        # Si on est proche du point intermédiaire, en chercher un nouveau
        dist_to_intermediate = math.sqrt(
            (self.x - self.point_intermediaire[0])**2 + 
            (self.y - self.point_intermediaire[1])**2
        )
        if dist_to_intermediate < RAYON_CERCLE:
            self.trouver_nouveau_point_intermediaire(portes, porte_cible)
                
        # Déplacement vers le point intermédiaire
        if self.point_intermediaire:
            dx = self.point_intermediaire[0] - self.x
            dy = self.point_intermediaire[1] - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                deplacement = min(33, distance)
                new_x = self.x + (dx/distance) * deplacement
                new_y = self.y + (dy/distance) * deplacement
                
                if (0 <= new_x <= LARGEUR and 
                    0 <= new_y <= HAUTEUR and 
                    not self.point_dans_zone_desactivee(new_x, new_y, portes)):
                    self.derniere_position = (self.x, self.y)
                    self.x = new_x
                    self.y = new_y
                    self.trace.append((int(self.x), int(self.y)))
                else:
                    self.trouver_nouveau_point_intermediaire(portes, porte_cible)
                
        if not self.chemin_bloque(porte_cible, portes):
            self.en_evitement = False
            self.point_intermediaire = None
            return self.deplacer_vers_point(porte_cible.pointA)
        
    def trouver_nouveau_point_intermediaire(self, portes, porte_cible):
        """Trouve un nouveau point intermédiaire pour l'évitement en cherchant le chemin le plus court"""
        angle_base = math.atan2(
            porte_cible.pointA[1] - self.y,
            porte_cible.pointA[0] - self.x
        )
        
        meilleur_point = None
        meilleure_distance = float('inf')
        distance_cible = math.sqrt(
            (porte_cible.pointA[0] - self.x)**2 + 
            (porte_cible.pointA[1] - self.y)**2
        )
        
        # Test sur plusieurs distances
        for distance_test in [RAYON_ZONE * 1.5, RAYON_ZONE * 2, RAYON_ZONE * 2.5]:
            # Test dans les deux sens de rotation
            for i in range(-6, 7):  # De -180° à +180° par pas de 30°
                angle_test = angle_base + (i * math.pi/6)
                
                test_x = self.x + math.cos(angle_test) * distance_test
                test_y = self.y + math.sin(angle_test) * distance_test
                
                # Vérifier si le point est valide
                if (0 <= test_x <= LARGEUR and 
                    0 <= test_y <= HAUTEUR and 
                    not self.point_dans_zone_desactivee(test_x, test_y, portes) and
                    not self.chemin_traverse_zone_desactivee(portes, (test_x, test_y))):
                    
                    # Calculer la distance totale du chemin (distance jusqu'au point + distance du point à la cible)
                    distance_point = math.sqrt((test_x - self.x)**2 + (test_y - self.y)**2)
                    distance_point_cible = math.sqrt(
                        (test_x - porte_cible.pointA[0])**2 + 
                        (test_y - porte_cible.pointA[1])**2
                    )
                    distance_totale = distance_point + distance_point_cible
                    
                    # Mettre à jour si c'est le meilleur chemin trouvé
                    if distance_totale < meilleure_distance:
                        meilleure_distance = distance_totale
                        meilleur_point = (test_x, test_y)
                        self.angle_actuel = angle_test
        
        if meilleur_point:
            self.point_intermediaire = meilleur_point
            return True
            
        return False

    def trouver_chemin_alternatif(self, portes, porte_cible):
        """Trouve un point intermédiaire pour contourner les obstacles"""
        angle_base = math.atan2(
            porte_cible.pointA[1] - self.y,
            porte_cible.pointA[0] - self.x
        )
        
        # Essayer différents angles pour trouver un chemin libre
        for i in range(12):  # Teste 12 directions différentes
            # Alterne entre angles positifs et négatifs croissants
            angle_test = angle_base + (i // 2 + 1) * ANGLE_ROTATION * (-1 if i % 2 else 1)
            distance_test = RAYON_ZONE * 1.5
            
            point_test_x = self.x + math.cos(angle_test) * distance_test
            point_test_y = self.y + math.sin(angle_test) * distance_test
            
            # Vérifier si ce point est valide
            if (0 <= point_test_x <= LARGEUR and 
                0 <= point_test_y <= HAUTEUR and
                not self.point_dans_zone_desactivee(point_test_x, point_test_y, portes)):
                return (point_test_x, point_test_y)
        
        return None
    
    def chemin_traverse_zone_desactivee(self, portes, point_cible):
        """Vérifie si le chemin vers un point traverse une zone désactivée"""
        points_verification = 10
        dx = point_cible[0] - self.x
        dy = point_cible[1] - self.y
        longueur = math.sqrt(dx*dx + dy*dy)
        
        if longueur == 0:
            return False
            
        dx, dy = dx/longueur, dy/longueur
        
        for i in range(points_verification):
            distance = (i + 1) * longueur / points_verification
            point_x = self.x + dx * distance
            point_y = self.y + dy * distance
            
            for porte in portes:
                if not porte.active:
                    if porte.distance_au_point(point_x, point_y) < RAYON_ZONE:
                        return True
        return False
    
    def point_dans_zone_desactivee(self, x, y, portes):
        """Vérifie si un point est dans une zone de porte désactivée"""
        for porte in portes:
            if not porte.active:
                distance = math.sqrt((x - porte.centre_x)**2 + (y - porte.centre_y)**2)
                if distance < RAYON_ZONE:
                    return True
        return False

    def calculer_prochain_deplacement(self, portes):
        # Vérifier si un cercle rouge (porte inactive) est sur le chemin
        for porte in portes:
            if not porte.active:  # Une porte inactive représente un "cercle rouge"
                if self.point_dans_zone_desactivee(self.x, self.y, portes):  # Si le drone est dans une zone rouge
                    self.eviter_cercle_rouge(porte, portes)  # Prioriser l'évitement
                    return True

        # Si le drone est déjà en traversée ou en mouvement post-traversée, ne rien faire d'autre
        if self.en_traversee or self.en_mouvement_post_traversee:
            return False

        # Trouver le point le plus proche (A ou B) parmi toutes les portes actives
        point_plus_proche = None
        distance_min = float('inf')
        porte_plus_proche = None

        for porte in portes:
            if not porte.active:
                continue

            # Calculer la distance au point A
            dist_a = math.sqrt((self.x - porte.pointA[0])**2 + (self.y - porte.pointA[1])**2)
            # Calculer la distance au point B
            dist_b = math.sqrt((self.x - porte.pointB[0])**2 + (self.y - porte.pointB[1])**2)

            # Si on est très proche d'un point, commencer la traversée
            if dist_a < RAYON_CERCLE or dist_b < RAYON_CERCLE:
                self.commencer_traversee(porte)
                return True

            # Mettre à jour le point le plus proche
            if dist_a < distance_min:
                distance_min = dist_a
                point_plus_proche = porte.pointA
                porte_plus_proche = porte
            if dist_b < distance_min:
                distance_min = dist_b
                point_plus_proche = porte.pointB
                porte_plus_proche = porte

        if not porte_plus_proche:
            return False

        # Vérifier si on doit contourner un obstacle
        if (self.chemin_bloque(porte_plus_proche, portes) or
            self.point_dans_zone_desactivee(self.x, self.y, portes)):
            self.contourner_obstacle(portes, porte_plus_proche)
        else:
            self.en_evitement = False
            self.point_intermediaire = None
            self.deplacer_vers_point(point_plus_proche)

        return True

    def chemin_bloque(self, porte_cible, portes):
        """Vérifie si le chemin direct vers la porte est bloqué par une zone désactivée"""
        points_verification = 20
        dx = porte_cible.pointA[0] - self.x
        dy = porte_cible.pointA[1] - self.y
        
        for i in range(points_verification):
            t = i / points_verification
            point_x = self.x + dx * t
            point_y = self.y + dy * t
            
            if self.point_dans_zone_desactivee(point_x, point_y, portes):
                return True
        return False

    def deplacer_vers_point(self, point):
        """Déplace le cercle vers un point donné"""
        dx = point[0] - self.x
        dy = point[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            deplacement = random.randint(MIN_DEPLACEMENT, MAX_DEPLACEMENT) / 10
            deplacement = min(deplacement, distance)
            new_x = self.x + (dx / distance) * deplacement
            new_y = self.y + (dy / distance) * deplacement
            
            # Vérifier que le nouveau point est dans les limites de l'écran
            self.x = min(max(new_x, RAYON_CERCLE), LARGEUR - RAYON_CERCLE)
            self.y = min(max(new_y, RAYON_CERCLE), HAUTEUR - RAYON_CERCLE)
            
            # Mettre à jour la trace avec la nouvelle position
            self.mettre_a_jour_trace((int(self.x), int(self.y)))
    
    def chemin_traverse_porte_desactivee(self, portes, point_cible):
        """Vérifie si le chemin direct vers la cible traverse une porte désactivée"""
        for porte in portes:
            if not porte.active:  # Vérifie seulement les portes désactivées
                # Calculer si la ligne entre la position actuelle et la cible intersecte
                # avec la zone de la porte désactivée
                dx = point_cible[0] - self.x
                dy = point_cible[1] - self.y
                distance_totale = math.sqrt(dx**2 + dy**2)
                
                # Vérifier plusieurs points le long du chemin
                for i in range(10):  # Vérifie 10 points le long du chemin
                    t = i / 10
                    point_x = self.x + dx * t
                    point_y = self.y + dy * t
                    if porte.distance_au_point(point_x, point_y) < RAYON_ZONE:
                        return True
        return False
    
    def eviter_cercle_rouge(self, cercle_rouge, portes):
        """
        Évite un cercle rouge sur le chemin du drone.
        """
        # Calculer la distance entre le drone et le centre du cercle rouge
        dx = cercle_rouge.centre_x - self.x
        dy = cercle_rouge.centre_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return  # Éviter la division par zéro

        # Déterminer le point d'entrée/sortie (périmètre du cercle rouge)
        point_s_e = (
            self.x + (dx / distance) * RAYON_ZONE,
            self.y + (dy / distance) * RAYON_ZONE
        )

        # Calculer les périmètres dans les deux directions
        angle_sortie = math.atan2(self.y - cercle_rouge.centre_y, self.x - cercle_rouge.centre_x)
        angle_intersection = math.atan2(point_s_e[1] - cercle_rouge.centre_y, point_s_e[0] - cercle_rouge.centre_x)
        t1 = (angle_intersection - angle_sortie) % (2 * math.pi)  # Sens horaire
        t2 = (angle_sortie - angle_intersection) % (2 * math.pi)  # Sens antihoraire

        # Choisir la direction (gauche ou droite) et avancer de 33 pixels après sortie
        if t2 < t1:
            # Tourner à gauche et avancer de 33 pixels
            self.tourner_et_avancer(-math.pi / 2, 33)
            while self.point_dans_zone_desactivee(self.x, self.y, portes):
                self.tourner_et_avancer(-3 * math.pi / 4, 33)  # Évitement supplémentaire
            # Forcer un déplacement de 33 pixels en sortie
            self.tourner_et_avancer(-math.pi / 2, 33)
        else:
            # Tourner à droite et avancer de 33 pixels
            self.tourner_et_avancer(math.pi / 2, 33)
            while self.point_dans_zone_desactivee(self.x, self.y, portes):
                self.tourner_et_avancer(3 * math.pi / 4, 33)  # Évitement supplémentaire
            # Forcer un déplacement de 33 pixels en sortie
            self.tourner_et_avancer(math.pi / 2, 33)

    def tourner_et_avancer(self, angle, distance):
        """
        Tourne le drone d'un angle donné et avance d'une distance.
        """
        # Calculer les déplacements en X et Y
        dx = math.cos(angle) * distance
        dy = math.sin(angle) * distance

        # Mettre à jour la position du drone
        self.x += dx
        self.y += dy

        # Ajouter la nouvelle position à la trace
        self.trace.append((int(self.x), int(self.y)))

    def est_sur_chemin(self, cercle_rouge, portes):
        """
        Vérifie si le cercle rouge est toujours sur le chemin du drone.
        """
        for porte in portes:
            if not porte.active:
                continue

            dx = porte.pointA[0] - self.x
            dy = porte.pointA[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= RAYON_ZONE and cercle_rouge.distance_au_point(self.x, self.y) < RAYON_ZONE:
                return True
        return False

    def commencer_traversee(self, porte):
        self.en_traversee = True
        self.porte_actuelle = porte

        # Déterminer quel point est le plus proche
        dist_a = math.sqrt((self.x - porte.pointA[0])**2 + (self.y - porte.pointA[1])**2)
        dist_b = math.sqrt((self.x - porte.pointB[0])**2 + (self.y - porte.pointB[1])**2)
        
        # On commence par le point le plus proche
        if dist_a <= dist_b:
            self.x = porte.pointA[0]
            self.y = porte.pointA[1]
            self.point_cible = porte.pointB
            porte.points_traverses.add((int(porte.pointA[0]), int(porte.pointA[1])))
        else:
            self.x = porte.pointB[0]
            self.y = porte.pointB[1]
            self.point_cible = porte.pointA
            porte.points_traverses.add((int(porte.pointB[0]), int(porte.pointB[1])))

        dx = self.point_cible[0] - self.x
        dy = self.point_cible[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        self.direction_traversee = {
            'dx': dx / distance,
            'dy': dy / distance
        }

        self.trace.append((int(self.x), int(self.y)))

    def continuer_traversee(self):
        if not self.en_traversee or not self.point_cible:
            return False

        dx = self.point_cible[0] - self.x
        dy = self.point_cible[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < VITESSE_TRAVERSEE:
            self.x = self.point_cible[0]
            self.y = self.point_cible[1]
            point_actuel = (int(self.x), int(self.y))
            self.mettre_a_jour_trace(point_actuel)  # Mettre à jour la trace
            self.porte_actuelle.points_traverses.add(point_actuel)

            if len(self.porte_actuelle.points_traverses) >= 2:
                self.porte_actuelle.active = False
                self.en_traversee = False
                self.en_mouvement_post_traversee = True
                self.direction_post_traversee = {
                    'dx': self.direction_traversee['dx'],
                    'dy': self.direction_traversee['dy'],
                    'distance_restante': DISTANCE_POST_TRAVERSEE
                }
                return True

            point_a = (int(self.porte_actuelle.pointA[0]), int(self.porte_actuelle.pointA[1]))
            point_b = (int(self.porte_actuelle.pointB[0]), int(self.porte_actuelle.pointB[1]))
            
            if point_actuel == point_a and point_b not in self.porte_actuelle.points_traverses:
                self.point_cible = self.porte_actuelle.pointB
            elif point_actuel == point_b and point_a not in self.porte_actuelle.points_traverses:
                self.point_cible = self.porte_actuelle.pointA

        vitesse = VITESSE_TRAVERSEE * 4
        self.x += (dx / distance) * vitesse
        self.y += (dy / distance) * vitesse
        self.mettre_a_jour_trace((int(self.x), int(self.y)))  # Mettre à jour la trace
        return False

    def continuer_mouvement_post_traversee(self):
        if not self.en_mouvement_post_traversee or not self.direction_post_traversee:
            return

        vitesse = 4
        distance_a_parcourir = min(vitesse, self.direction_post_traversee['distance_restante'])
        
        self.x += self.direction_post_traversee['dx'] * distance_a_parcourir
        self.y += self.direction_post_traversee['dy'] * distance_a_parcourir
        
        self.direction_post_traversee['distance_restante'] -= distance_a_parcourir
        
        self.mettre_a_jour_trace((int(self.x), int(self.y)))  # Mettre à jour la trace
        
        if self.direction_post_traversee['distance_restante'] <= 0:
            self.en_mouvement_post_traversee = False
            self.direction_post_traversee = None

    def dessiner(self):
        # Dessiner la trace
        if len(self.trace) > 1:
            pygame.draw.lines(ecran, NOIR, False, self.trace, 2)
        
        # Dessiner le cercle
        pygame.draw.circle(ecran, NOIR, (int(self.x), int(self.y)), RAYON_CERCLE)
        
        # Afficher le compteur de distance
        font = pygame.font.Font(None, 28)
        distance_text = f"Distance: {int(self.distance_totale)} pixels"
        text_surface = font.render(distance_text, True, NOIR)
        ecran.blit(text_surface, (10, 10))

# Création des portes manuellement
portes = [
    Porte(BLEU, x1=714, y1=179, angle=0.0),
    Porte(ROUGE, x1=510, y1=302, angle=0.0),
]

# Vérifiez si toutes les portes sont placées avec succès
for porte in portes:
    if not porte.placement_reussi:
        print("Impossible de placer une porte manuellement.")
        pygame.quit()
        exit()

# Création du cercle avec la position initiale à 500,33
cercle = Cercle(portes)

# Boucle principale (inchangée)
en_cours = True
horloge = pygame.time.Clock()

while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    if cercle.en_traversee:
        if cercle.continuer_traversee():
            cercle.portes_traversees += 1
    elif cercle.en_mouvement_post_traversee:
        cercle.continuer_mouvement_post_traversee()
    else:
        cercle.calculer_prochain_deplacement(portes)

    # Maintenir le cercle dans les limites de l'écran
    cercle.x = min(max(cercle.x, 0), LARGEUR)
    cercle.y = min(max(cercle.y, 0), HAUTEUR)

    # Dessiner
    ecran.fill(BLANC)
    for porte in portes:
        porte.dessiner()
    cercle.dessiner()
    pygame.display.flip()
    
    horloge.tick(60)