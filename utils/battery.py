import time
import threading

class BatteryMonitoring:
    """
    Classe pour surveiller le niveau de batterie du drone en temps réel.

    Attributes:
        drone: L'instance du contrôleur du drone, qui fournit l'accès aux méthodes du drone.
        battery_level: Le niveau actuel de la batterie du drone (initialement "N/A" jusqu'à la première mise à jour).
    """

    def __init__(self, drone):
        """
        Initialise le moniteur de batterie avec une référence au contrôleur du drone.

        Args:
            drone: L'objet du contrôleur du drone.
        """
        self.drone = drone
        self.battery_level = "N/A"
    
    def start_monitoring(self):
        """
        Démarre un thread pour mettre à jour le niveau de batterie en continu.
        Le thread s'exécute en arrière-plan.
        """
        thread = threading.Thread(target=self.update_battery, daemon=True)
        thread.start()

    def update_battery(self):
        """
        Met à jour le niveau de batterie toutes les 10 secondes en accédant aux données du drone.
        En cas d'erreur de communication avec le drone, affiche un message d'erreur.
        """
        while True:
            try:
                self.battery_level = self.drone.tello.get_battery()
            except Exception as e:
                print(f"Erreur de batterie: {e}")
            time.sleep(10)
