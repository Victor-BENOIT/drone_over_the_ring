import time
import threading

class BatteryMonitoring:
    def __init__(self, drone):
        self.drone = drone
        self.battery_level = "N/A"
    
    def start_monitoring(self):
        thread = threading.Thread(target=self.update_battery, daemon=True)
        thread.start()

    def update_battery(self):
        while True:
            try:
                self.battery_level = self.drone.tello.get_battery()
            except Exception as e:
                print(f"Erreur de batterie: {e}")
            time.sleep(10)

