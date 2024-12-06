import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from drone_path_calculator import DronePathCalculator

class DroneApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drone Path Calculator")
        
        self.log_path = "modes/followmode/log_test_curve.txt"
        
        # Charger les données et afficher les résultats
        self.launch_path_calculation()
    
    def launch_path_calculation(self):
        """Lance le calcul du chemin et ouvre une fenêtre avec les résultats."""
        # Créer une instance de DronePathCalculator
        calculator = DronePathCalculator(self.log_path)
        calculator.lecture_log()
        calculator.calculer_coordonnees()
        
        # Afficher les résultats
        self.display_results(calculator.data)
    
    def display_results(self, data):
        """Affiche une fenêtre avec les résultats et un graphe 3D."""
        results_window = self.master  # Utiliser la fenêtre principale
        results_window.title("Résultats des calculs")
        
        # Cadre pour les coordonnées
        coords_frame = tk.Frame(results_window)
        coords_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        coords_label = tk.Label(coords_frame, text="Coordonnées des points:")
        coords_label.pack()
        
        coords_text = tk.Text(coords_frame, height=20, width=50)
        for item in data:
            mouvement_type, points = item
            coords_text.insert(tk.END, f"{mouvement_type}:\n")
            for point in points:
                coords_text.insert(tk.END, f"  x={point[0]}, y={point[1]}, z={point[2]}\n")
        coords_text.pack()
        
        # Bouton Décollage
        takeoff_button = ttk.Button(
            coords_frame,
            text="Décollage",
            command=self.takeoff
        )
        takeoff_button.pack(pady=10)
        
        # Cadre pour le graphe 3D
        graph_frame = tk.Frame(results_window)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        figure = plt.Figure(figsize=(5, 5), dpi=100)
        ax = figure.add_subplot(111, projection='3d')
        
        # Variables pour stocker les données pour le graphe
        x_data = []
        y_data = []
        z_data = []
        
        # Ajouter les mouvements dans le graphique
        for item in data:
            mouvement_type, points = item
            if mouvement_type == "point":
                x_data.append(points[0][0])
                y_data.append(points[0][1])
                z_data.append(points[0][2])
                ax.scatter(points[0][0], points[0][1], points[0][2], c='g', marker='o')  # Point vert
            elif mouvement_type == "straight line":
                for i in range(1, len(points)):
                    ax.plot([points[i-1][0], points[i][0]], 
                            [points[i-1][1], points[i][1]], 
                            [points[i-1][2], points[i][2]], c='b')  # Lignes droites bleues
            elif mouvement_type == "curve":
                # Ajouter une courbe en plusieurs segments
                for i in range(1, len(points)-1):
                    ax.plot([points[i-1][0], points[i][0], points[i+1][0]], 
                            [points[i-1][1], points[i][1], points[i+1][1]], 
                            [points[i-1][2], points[i][2], points[i+1][2]], c='r')  # Courbe rouge

        ax.set_xlabel('X (mètres)')
        ax.set_ylabel('Y (mètres)')
        ax.set_zlabel('Z (mètres)')
        ax.set_title("Trajectoire du drone")
        
        # Définir les limites des axes pour un espace de 5m x 5m x 5m
        ax.set_xlim([-5, 5])  # En mètres
        ax.set_ylim([-5, 5])  # En mètres
        ax.set_zlim([-5, 5])  # En mètres
        
        # Ajouter des ticks tous les mètres
        ax.set_xticks(range(-5, 6, 1))  # Chaque mètre
        ax.set_yticks(range(-5, 6, 1))
        ax.set_zticks(range(-5, 6, 1))
        
        canvas = FigureCanvasTkAgg(figure, master=graph_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def takeoff(self):
        """Action déclenchée lors du clic sur le bouton 'Décollage'."""
        print("Décollage effectué !")  # Remplacez par les commandes de décollage du drone.


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneApp(root)
    root.mainloop()
