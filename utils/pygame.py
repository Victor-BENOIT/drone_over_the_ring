import pygame
import threading
import cv2
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, BATTERY_DISPLAY_X, BATTERY_DISPLAY_Y, BATTERY_DISPLAY_WIDTH, BATTERY_DISPLAY_HEIGHT, DIST_DISPLAY_X, DIST_DISPLAY_Y, DIST_DISPLAY_WIDTH, DIST_DISPLAY_HEIGHT

class PygameDisplay: 
    def __init__(self, drone, battery_monitoring):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.drone = drone
        self.battery_monitoring = battery_monitoring
        self.running = True

    def start_display_thread(self):
        thread = threading.Thread(target=self.update_display, daemon=True)
        thread.start()
        return thread
    
    def update_display(self):
        while self.running:
            self.handle_events()
            self.display_target(self.drone.target.get_target_window())
            self.display_distance(self.drone.vision.distance)
            self.display_battery()
            self.display_frame(self.drone.get_frame())
            self.display_gates()
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("Emergency landing!")
                self.running = False
                pygame.quit()
                return False
            if event.type == pygame.QUIT:
                self.running = False
                return False
        return True
    
    def display_frame(self, frame):
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Ajuster l'orientation si nécessaire
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Afficher la frame sur l'écran
        self.screen.blit(frame_surface, (0, 0))

    def display_battery(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (BATTERY_DISPLAY_X, BATTERY_DISPLAY_Y, BATTERY_DISPLAY_WIDTH, BATTERY_DISPLAY_HEIGHT))
        battery_text = self.font.render(f"Batterie: {self.battery_monitoring.battery_level}%", True, (255, 255, 255))
        self.screen.blit(battery_text, (BATTERY_DISPLAY_X + 5, BATTERY_DISPLAY_Y + 5))
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

    def display_gates(self):
        for gate in self.drone.vision.gates:
            x1, y1, w, h, score, class_id = gate
            new_x1 = SCREEN_WIDTH - (x1 + w)
            pygame.draw.rect(self.screen, (0, 255, 0), (new_x1, y1, w, h), 4)
            score_text = self.font.render(str(class_id) + f" : {score:.2f}", True, (0, 255, 0))
            self.screen.blit(score_text, (new_x1, y1 - 20))
    
    def quit(self):
        pygame.quit()