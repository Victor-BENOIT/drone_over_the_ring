import pygame
import re
from djitellopy import Tello
import time

class DroneInterface:
    def __init__(self, log_path):
        self.log_path = log_path
        self.donnees = []

        # Pygame setup
        pygame.init()
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Follow Mode")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.bouton_etat = "Décollage"

        # Console setup
        self.console = Console(20, 0, self.screen_width - 40, 0, self.font)
        
        self.donnees_sommees = []
        self.tello = Tello()

        # Button properties
        self.bouton_x, self.bouton_y = 300, 500
        self.bouton_width, self.bouton_height = 200, 50
        self.bouton_color = (100, 100, 100)
        self.bouton_text_color = (255, 255, 255)
        self.bouton_clique = False

    def lecture_log(self):
        """Lecture du fichier log."""
        with open(self.log_path, 'r') as file:
            for line in file:
                line = line.strip()
                if re.match(r'^(up|down|forward|backward|left|right|rotate_counter_clockwise|rotate_clockwise) \d+', line):
                    mouvement, valeur = line.split()
                    self.donnees.append([mouvement, int(valeur), None])
                elif line.startswith("GATE_IN_FRONT"):
                    _, gate_type = line.split()
                    self.donnees.append(["GATE_IN_FRONT", None, gate_type])

    def compense_mouvements(self):
        """Compensation des mouvements consécutifs opposés avec gestion des rotations intermédiaires."""
        somme_actuelle = {key: 0 for key in ["up", "down", "left", "right", "forward", "backward", 
                                            "rotate_counter_clockwise", "rotate_clockwise"]}
        dernier_mouvement = None

        def ajout_mouvements_compenses():
            up_down = somme_actuelle["up"] - somme_actuelle["down"]
            left_right = somme_actuelle["left"] - somme_actuelle["right"]
            forward_backward = somme_actuelle["forward"] - somme_actuelle["backward"]
            rotations = somme_actuelle["rotate_counter_clockwise"] - somme_actuelle["rotate_clockwise"]

            valeurs_temp = []
            if up_down != 0:
                valeurs_temp.append(["up" if up_down > 0 else "down", abs(up_down), None])
            if left_right != 0:
                valeurs_temp.append(["left" if left_right > 0 else "right", abs(left_right), None])
            if forward_backward != 0:
                valeurs_temp.append(["forward" if forward_backward > 0 else "backward", abs(forward_backward), None])
            if rotations != 0:
                valeurs_temp.append(["rotate_counter_clockwise" if rotations > 0 else "rotate_clockwise", abs(rotations), None])

            valeurs_temp.sort(key=lambda x: ["rotate_counter_clockwise", "rotate_clockwise", "up", "down", "left", "right", "forward", "backward"].index(x[0]))
            self.donnees_sommees.extend(valeurs_temp)

        for entry in self.donnees:
            if entry[0] == "GATE_IN_FRONT":
                ajout_mouvements_compenses()
                somme_actuelle = {key: 0 for key in somme_actuelle}
                dernier_mouvement = None
                self.donnees_sommees.append(entry)
            else:
                mouvement, valeur, _ = entry

                # Si un mouvement de rotation est rencontré, on ajoute les mouvements actuels
                if mouvement in ["rotate_counter_clockwise", "rotate_clockwise"]:
                    ajout_mouvements_compenses()
                    somme_actuelle = {key: 0 for key in somme_actuelle}
                    dernier_mouvement = mouvement
                    self.donnees_sommees.append(entry)
                else:
                    if dernier_mouvement in ["rotate_counter_clockwise", "rotate_clockwise"]:
                        ajout_mouvements_compenses()
                        somme_actuelle = {key: 0 for key in somme_actuelle}

                    somme_actuelle[mouvement] += valeur
                    dernier_mouvement = mouvement

        ajout_mouvements_compenses()


    def execute_mouvements(self):
        """Exécution des mouvements via le drone."""
        command_map = {
            "up": self.tello.move_up,
            "down": self.tello.move_down,
            "forward": self.tello.move_forward,
            "backward": self.tello.move_back,
            "left": self.tello.move_left,
            "right": self.tello.move_right,
            "rotate_counter_clockwise": self.tello.rotate_counter_clockwise,
            "rotate_clockwise": self.tello.rotate_clockwise,
        }

        for mouvement in self.donnees_sommees:
            if mouvement[0] == "GATE_IN_FRONT":
                message = f"Porte détectée: {mouvement[2]}"
                self.console.add_message(message)
                self.console.draw(self.screen)  # Redessiner la console     
                time.sleep(2)
            else:
                commande, valeur, _ = mouvement
                if commande in command_map:
                    message = f"Execution: {commande} {valeur}"
                    self.console.add_message(message)
                    self.console.draw(self.screen)  # Redessiner la console
                    command_map[commande](valeur)
                    time.sleep(1)
                else:
                    self.console.add_message(f"Commande inconnue: {commande}")
                    self.console.draw(self.screen)  # Redessiner la console



    def affichage_interface(self, data, x, y, width, titre):
        """Affichage d'un tableau avec les données."""
        header_color = (60, 60, 60)
        row_color_light = (80, 80, 80)
        row_color_dark = (60, 60, 60)
        text_color = (255, 255, 255)

        pygame.draw.rect(self.screen, header_color, (x, y, width, 30))
        titre_surface = self.font.render(titre, True, text_color)
        self.screen.blit(titre_surface, (x + 10, y + 5))

        row_height = 30
        for i, row in enumerate(data):
            rect_color = row_color_light if i % 2 == 0 else row_color_dark
            pygame.draw.rect(self.screen, rect_color, (x, y + 30 + i * row_height, width, row_height))

            for j, cell in enumerate(row):
                if j == 0 and cell:  # Modifier uniquement la première colonne (type de mouvement)
                    if cell == "rotate_counter_clockwise":
                        cell_text = "rotate_CCW"
                    elif cell == "rotate_clockwise":
                        cell_text = "rotate_CW"
                    else:
                        cell_text = str(cell)
                else:
                    cell_text = str(cell) if cell is not None else ""

                text_surface = self.font.render(cell_text, True, text_color)
                self.screen.blit(text_surface, (x + 10 + j * (width // 3), y + 30 + i * row_height + 5))


    def dessiner_bouton(self, x, y, width, height):
        """Affichage d'un bouton."""
        pygame.draw.rect(self.screen, self.bouton_color, (x, y, width, height))
        text_surface = self.font.render(self.bouton_etat, True, self.bouton_text_color)  # Utiliser self.bouton_etat
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        """Boucle principale de l'application."""
        try:
            self.tello.connect()
            self.lecture_log()
            self.compense_mouvements()

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if (self.bouton_x <= mouse_x <= self.bouton_x + self.bouton_width and
                            self.bouton_y <= mouse_y <= self.bouton_y + self.bouton_height and not self.bouton_clique):
                            self.bouton_clique = True
                            self.bouton_etat = "En vol"
                            self.bouton_color = (70, 70, 70)
                            self.dessiner_bouton(self.bouton_x, self.bouton_y, self.bouton_width, self.bouton_height)
                            self.console.add_message("Décollage initié !")
                            self.console.draw(self.screen)
                            self.tello.takeoff()
                            self.execute_mouvements()
                            self.tello.land()
                            self.console.add_message("Atterrissage effectué !")
                            self.bouton_etat = "Manoeuvre  terminée"
                            self.dessiner_bouton(self.bouton_x, self.bouton_y, self.bouton_width, self.bouton_height)


                self.screen.fill((40, 40, 40))
                self.affichage_interface(self.donnees, 20, 20, 360, "Mouvements du fichier")
                self.affichage_interface(self.donnees_sommees, 420, 20, 360, "Mouvements optimisés")
                self.console.draw(self.screen)
                self.dessiner_bouton(self.bouton_x, self.bouton_y, self.bouton_width, self.bouton_height)
                pygame.display.flip()
                self.clock.tick(10)
        finally:
            self.tello.end()
            pygame.quit()


class Console:
    def __init__(self, x, y, width, height, font, max_lines=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.max_lines = max_lines
        self.messages = []
        self.bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)

    def add_message(self, message):
        """Ajoute un message à la console et gère l'historique."""
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)

    def draw(self, screen):
        """Affiche la console sur l'écran."""
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        line_height = self.font.get_linesize()
        for i, message in enumerate(self.messages):
            text_surface = self.font.render(message, True, self.text_color)
            screen.blit(text_surface, (self.x + 5, self.y + 5 + i * line_height))
        pygame.display.flip()    


if __name__ == "__main__":
    interface = DroneInterface("log_test.txt")
    interface.run()
