from drone_controller.drone import DroneController
from utils.battery import BatteryMonitoring
from utils.pygame import PygameDisplay

# Initialisation du drone
drone = DroneController()
battery_monitoring = BatteryMonitoring(drone)
pygame_window = PygameDisplay()

def start_drone_control():

    battery_monitoring.start_monitoring()
    drone.mode.start()

    running = True
    while running:
        running = pygame_window.handle_events() #Gère les événements et l'interruption
        drone.vision.process_frame(drone.get_frame(), pygame_window.screen)
        pygame_window.display_target(drone.target.get_target_window())
        pygame_window.display_battery(battery_monitoring.battery_level)
        drone.mode.main_loop()

    drone.mode.stop()
if __name__ == "__main__":
    try:
        start_drone_control()
    finally:
        drone.stop_video_stream()
        pygame_window.quit()