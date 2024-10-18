import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, BATTERY_DISPLAY_X, BATTERY_DISPLAY_Y, BATTERY_DISPLAY_WIDTH, BATTERY_DISPLAY_HEIGHT, DIST_DISPLAY_X, DIST_DISPLAY_Y, DIST_DISPLAY_WIDTH, DIST_DISPLAY_HEIGHT

class PygameDisplay: 
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("Emergency landing!")
                pygame.quit()
                return False
            if event.type == pygame.QUIT:
                return False  # Indique que la fenêtre doit être fermée
        return True  # Continue l'exécution

    def display_battery(self, battery):
        pygame.draw.rect(self.screen, (0, 0, 0), (BATTERY_DISPLAY_X, BATTERY_DISPLAY_Y, BATTERY_DISPLAY_WIDTH, BATTERY_DISPLAY_HEIGHT)) # 795 15 155 50
        battery_text = self.font.render(f"Batterie: {battery}%", True, (255, 255, 255))
        self.screen.blit(battery_text, (BATTERY_DISPLAY_X + 5, BATTERY_DISPLAY_Y + 5))  # Position top right 800 20
        pygame.display.update()
    
    def display_distance(self, distance):
        pygame.draw.rect(self.screen, (0, 0, 0), (DIST_DISPLAY_X, DIST_DISPLAY_Y, DIST_DISPLAY_WIDTH, DIST_DISPLAY_HEIGHT)) # 15 15 180 50
        if distance == None:
            distance_text = self.font.render(f"Distance: {distance}", True, (255, 255, 255))
        else:
            distance_text = self.font.render(f"Distance: {distance}cm", True, (255, 255, 255))
        self.screen.blit(distance_text, (DIST_DISPLAY_X + 5, DIST_DISPLAY_Y + 5))  # Position top left 20 20
        pygame.display.update()

    def display_target(self, target):
        pygame.draw.rect(self.screen, (255, 0, 0), target, 5)
        pygame.display.update()
    
    def quit(self):
        pygame.quit()