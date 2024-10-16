import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

class PygameDisplay: 
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Indique que la fenêtre doit être fermée
        return True  # Continue l'exécution

    def display_battery(self, battery):
        pygame.draw.rect(self.screen, (0, 0, 0), (795, 15, 155, 50))
        battery_text = self.font.render(f"Batterie: {battery}%", True, (255, 255, 255))
        self.screen.blit(battery_text, (800, 20))  # Position top right
        pygame.display.update()
    
    def display_distance(self, distance):
        pygame.draw.rect(self.screen, (0, 0, 0), (15, 15, 180, 50))
        if distance == None:
            distance_text = self.font.render(f"Distance: {distance}", True, (255, 255, 255))
        else:
            distance_text = self.font.render(f"Distance: {distance}cm", True, (255, 255, 255))
        self.screen.blit(distance_text, (20, 20))  # Position top left
        pygame.display.update()

    def display_target(self, target):
        pygame.draw.rect(self.screen, (255, 0, 0), target, 5)
        pygame.display.update()
    
    def quit(self):
        pygame.quit()