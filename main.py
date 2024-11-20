from drone_controller.drone import DroneController
from utils.battery import BatteryMonitoring
from utils.pygame import PygameDisplay

# Initialisation du drone
drone = DroneController()
battery_monitoring = BatteryMonitoring(drone)
pygame_window = PygameDisplay(drone, battery_monitoring)

def start_drone_control():
    """
    Démarre le contrôle du drone, le monitoring de la batterie et l'affichage de Pygame.

    Cette fonction initialise le monitoring de la batterie, lance le thread d'affichage Pygame,
    et commence la boucle principale du drone.
    Elle gère les événements, effectue le traitement vidéo et lance la boucle de contrôle du mode du drone.
    """
    battery_monitoring.start_monitoring()
    pygame_thread = pygame_window.start_display_thread()
    drone.mode.start()

    running = True
    while running:
        running = pygame_window.handle_events()
        drone.vision.process_frame(drone.get_frame())
        drone.mode.main_loop()

    pygame_thread.join()
    
    drone.mode.stop()

if __name__ == "__main__":
    try:
        start_drone_control()
    finally:
        # Sauvegarde des logs et arrêt des services
        drone.logging.save_logs()
        drone.mode.stop()
        drone.stop_video_stream()
