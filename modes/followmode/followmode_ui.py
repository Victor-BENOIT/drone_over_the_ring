import tkinter as tk
from tkinter import ttk
import numpy as np
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
        calculator.creation_path_cartesien()
        
        # Afficher les résultats
        self.display_results(calculator.coord_cart, calculator.gates_cart)
    
    def display_results(self, coord_cart, gates_cart):
        """Affiche une fenêtre avec les résultats et un graphe 3D."""
        results_window = self.master  # Utiliser la fenêtre principale
        results_window.title("Résultats des calculs")
        
        # Cadre pour les coordonnées
        coords_frame = tk.Frame(results_window)
        coords_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        coords_label = tk.Label(coords_frame, text="Coordonnées des points:")
        coords_label.pack()
        
        coords_text = tk.Text(coords_frame, height=20, width=50)
        for item in coord_cart:
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
        x_coord_cart = []
        y_coord_cart = []
        z_coord_cart = []
        
        # Ajouter les mouvements dans le graphique
        for item in coord_cart:
            mouvement_type, points = item
            if mouvement_type == "point":
                x_coord_cart.append(points[0][0] / 100)  # Convertir en mètres
                y_coord_cart.append(points[0][1] / 100)
                z_coord_cart.append(points[0][2] / 100)
                ax.scatter(points[0][0] / 100, points[0][1] / 100, points[0][2] / 100, c='g', marker='o')  # Point vert
            elif mouvement_type == "straight line":
                for i in range(1, len(points)):
                    # Convertir les coordonnées en mètres pour le graphique
                    ax.plot([points[i-1][0] / 100, points[i][0] / 100], 
                            [points[i-1][1] / 100, points[i][1] / 100], 
                            [points[i-1][2] / 100, points[i][2] / 100], c='b')  # Lignes droites bleues
            elif mouvement_type == "curve":
                # Ajouter une courbe en plusieurs segments
                for i in range(1, len(points)-1):
                    # Convertir les coordonnées en mètres pour le graphique
                    ax.plot([points[i-1][0] / 100, points[i][0] / 100, points[i+1][0] / 100], 
                            [points[i-1][1] / 100, points[i][1] / 100, points[i+1][1] / 100], 
                            [points[i-1][2] / 100, points[i][2] / 100, points[i+1][2] / 100], c='r')  # Courbe rouge


        for gate in gates_cart:
            gate_type, angle, center = gate
            cx, cy, cz = [c / 100 for c in center]  # Convertir en mètres

            if gate_type == "hoop":
                # Tracer un cercle dans le plan XY à une hauteur constante Z
                theta = np.linspace(0, 2 * np.pi, 100)
                x = 0.3 * np.cos(theta) + cx  # Rayon 0.3 m
                y = 0.3 * np.sin(theta) + cy
                z = np.full_like(x, cz)  # Constante sur Z
                ax.plot(x, y, z, color='blue', label='Hoop')


            elif gate_type == "hex":
                # Tracer un hexagone dans le plan XY à une hauteur constante Z
                theta = np.linspace(0, 2 * np.pi, 6, endpoint=True)  # 6 côtés
                x = 0.325 * np.cos(theta) + cx  # Rayon 0.325 m
                y = 0.325 * np.sin(theta) + cy
                z = np.full_like(x, cz)  # Constante sur Z
                ax.plot(x, y, z, color='orange', label='Hexagon')

        
        ax.set_xlabel('X (mètres)')
        ax.set_ylabel('Y (mètres)')
        ax.set_zlabel('Z (mètres)')
        ax.set_title("Trajectoire du drone")
        
        # Définir les limites initiales des axes
        ax.set_xlim([-5, 5])
        ax.set_ylim([0, 5])
        ax.set_zlim([0, 5])
        
        canvas = FigureCanvasTkAgg(figure, master=graph_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        # Fonction de zoom à la molette
        def on_scroll(event):
            scale_factor = 1.2 if event.button == 'up' else 1 / 1.2  # Zoom in ou out
            ax.set_xlim([scale_factor * limit for limit in ax.get_xlim()])
            ax.set_ylim([scale_factor * limit for limit in ax.get_ylim()])
            ax.set_zlim([scale_factor * limit for limit in ax.get_zlim()])
            canvas.draw()

        # Connecter la molette au graphique
        canvas.mpl_connect("scroll_event", on_scroll)

    def takeoff(self):
        """Action déclenchée lors du clic sur le bouton 'Décollage'."""
        print("Décollage effectué !")  # Remplacez par les commandes de décollage du drone.


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneApp(root)
    root.mainloop()
