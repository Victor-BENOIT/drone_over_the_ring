import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import time      
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from drone_path_calculator import DronePathCalculator
from drone_connector import DroneConnector

class DroneApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drone Path Calculator")
        
        self.log_path = "modes/followmode/log_test_curve2.txt"

        self.connector = DroneConnector()

        self.coord_cart = []
        self.current_move_index = 0
        self.figure2 = None
        self.ax2 = None
        
        # Charger les données et afficher les résultats
        self.launch_path_calculation()
    
    def launch_path_calculation(self):
        """Lance le calcul du chemin et ouvre une fenêtre avec les résultats."""
        # Créer une instance de DronePathCalculator
        calculator = DronePathCalculator(self.log_path)
        calculator.lecture_log()
        calculator.calculer_coordonnees()
        calculator.creation_path_cartesien()

        self.coord_cart = calculator.coord_cart
        self.coord_relat  = calculator.matrice_coordonnees
        self.gate_types = calculator.gate_types

        # print(self.gate_types)
        # print(self.coord_relat)
        
        # Afficher les résultats
        self.display_results(self.coord_cart, calculator.gates_cart)
    
    def display_results(self, coord_cart, gates_cart):
        """Affiche une fenêtre avec les résultats et deux graphes 3D."""
        results_window = self.master  # Utiliser la fenêtre principale
        results_window.title("Résultats des calculs")

        # Cadre pour les coordonnées
        coords_frame = tk.Frame(results_window)
        coords_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        coords_label = tk.Label(coords_frame, text="Coordonnées cartésiennes:")
        coords_label.pack()

        coords_text = tk.Text(coords_frame, height=20, width=30)
        for item in coord_cart:
            mouvement_type, points = item
            coords_text.insert(tk.END, f"{mouvement_type}:\n")
            for point in points:
                coords_text.insert(tk.END, f"  x={point[0]}, y={point[1]}, z={point[2]}\n")
        coords_text.pack()

        # Bouton Connexion
        self.connect_button = ttk.Button(
            coords_frame,
            text="Connexion",
            command=self.drone_connect,
            style="Connect.TButton"
        )
        style = ttk.Style()
        style.configure("Connect.TButton", foreground="blue", background="blue")
        self.connect_button.pack(pady=10)

        # Bouton Décollage
        self.takeoff_button = ttk.Button(
            coords_frame,
            text="Décollage",
            command=self.takeoff,
            style="Takeoff.TButton"
        )
        style = ttk.Style()
        style.configure("Takeoff.TButton", foreground="blue", background="blue")
        self.takeoff_button.pack(pady=10)

        # Cadre pour les graphes 3D
        graph_frame = tk.Frame(results_window)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        figure1 = plt.Figure(figsize=(5, 5), dpi=100)
        ax1 = figure1.add_subplot(111, projection='3d')
        figure2 = plt.Figure(figsize=(5, 5), dpi=100)
        self.figure2 = figure2
        ax2 = figure2.add_subplot(111, projection='3d')
        self.ax2 = ax2

        # Variables pour stocker les données pour les graphes
        x_coord_cart = []
        y_coord_cart = []
        z_coord_cart = []

        # Ajouter les mouvements dans le graphique 1 (parcours généré)
        for item in coord_cart:
            mouvement_type, points = item
            if mouvement_type == "point":
                x_coord_cart.append(points[0][0] / 100)  # Convertir en mètres
                y_coord_cart.append(points[0][1] / 100)
                z_coord_cart.append(points[0][2] / 100)
                ax1.scatter(points[0][0] / 100, points[0][1] / 100, points[0][2] / 100, c='g', marker='o')  # Point vert
            elif mouvement_type == "straight line":
                for i in range(1, len(points)):
                    ax1.plot([points[i-1][0] / 100, points[i][0] / 100], 
                             [points[i-1][1] / 100, points[i][1] / 100], 
                             [points[i-1][2] / 100, points[i][2] / 100], c='b')  # Lignes droites bleues
            elif mouvement_type == "curve":
                for i in range(1, len(points)-1):
                    ax1.plot([points[i-1][0] / 100, points[i][0] / 100, points[i+1][0] / 100], 
                             [points[i-1][1] / 100, points[i][1] / 100, points[i+1][1] / 100], 
                             [points[i-1][2] / 100, points[i][2] / 100, points[i+1][2] / 100], c='r')  # Courbe rouge

        # Ajouter les gates dans les deux graphiques
        for gate in gates_cart:
            gate_type, angle, center = gate
            cx, cy, cz = [c / 100 for c in center]  # Convertir en mètres

            if gate_type == "hoop":
                theta = np.linspace(0, 2 * np.pi, 100)
                if angle in [0, 180]:
                    y = 0.3 * np.cos(theta) + cy  # Rayon 0.3 m
                    z = 0.3 * np.sin(theta) + cz
                    x = np.full_like(y, cx)
                elif angle in [90, 270]:
                    x = 0.3 * np.cos(theta) + cx  # Rayon 0.3 m
                    z = 0.3 * np.sin(theta) + cz
                    y = np.full_like(x, cy)
                ax1.plot(x, y, z, color='blue', label='Hoop')
                ax2.plot(x, y, z, color='blue', label='Hoop')

            elif gate_type == "hex":
                theta = np.linspace(0, 2 * np.pi, 6, endpoint=True)  # 6 côtés
                if angle in [0, 180]:
                    y = 0.325 * np.cos(theta) + cy
                    z = 0.325 * np.sin(theta) + cz
                    x = np.full_like(y, cx)
                elif angle in [90, 270]:
                    x = 0.325 * np.cos(theta) + cx
                    z = 0.325 * np.sin(theta) + cz
                    y = np.full_like(x, cy)
                ax1.plot(x, y, z, color='orange', label='Hexagon')
                ax2.plot(x, y, z, color='orange', label='Hexagon')

        # Configuration des graphiques
        ax1.set_xlabel('X (mètres)')
        ax1.set_ylabel('Y (mètres)')
        ax1.set_zlabel('Z (mètres)')
        ax1.set_title("Trajectoire générée")
        ax1.set_xlim([-5, 5])
        ax1.set_ylim([0, 5])
        ax1.set_zlim([0, 5])

        ax2.set_xlabel('X (mètres)')
        ax2.set_ylabel('Y (mètres)')
        ax2.set_zlabel('Z (mètres)')
        ax2.set_title("Trajectoire actuelle")
        ax2.set_xlim([-5, 5])
        ax2.set_ylim([0, 5])
        ax2.set_zlim([0, 5])

        # Création des canvases
        canvas1 = FigureCanvasTkAgg(figure1, master=graph_frame)
        canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas1.draw()

        canvas2 = FigureCanvasTkAgg(figure2, master=graph_frame)
        canvas2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        canvas2.draw()

        # Fonction de zoom à la molette
        def on_scroll(event):
            scale_factor = 1.2 if event.button == 'up' else 1 / 1.2  # Zoom in ou out
            for ax in [ax1, ax2]:
                ax.set_xlim([scale_factor * limit for limit in ax.get_xlim()])
                ax.set_ylim([scale_factor * limit for limit in ax.get_ylim()])
                ax.set_zlim([scale_factor * limit for limit in ax.get_zlim()])
            canvas1.draw()
            canvas2.draw()

        # Connecter la molette aux graphiques
        canvas1.mpl_connect("scroll_event", on_scroll)
        canvas2.mpl_connect("scroll_event", on_scroll)

    def update_button(self, type, text, couleur):
        style = ttk.Style()
        if type == "connect_button":
            self.connect_button.config(text=text)
            style.configure("Connect.TButton", foreground=couleur, background=couleur)
            self.connect_button.pack(pady=10)
            root.update_idletasks() 
            root.update()
        elif type == "takeoff_button":
            self.takeoff_button.config(text=text)
            style.configure("Takeoff.TButton", foreground=couleur, background=couleur)
            self.takeoff_button.pack(pady=10)
            root.update_idletasks() 
            root.update()
        else:
            return

    def takeoff(self):
        """Action déclenchée lors du clic sur le bouton 'Décollage'."""
        self.update_button("takeoff_button", "Démarrage du plan de vol", "black")
        if self.connector.connected:
            # self.draw_mouvement_step_by_step()
            self.execute_mouvement()
            self.update_button("takeoff_button", "Atterrissage", "black")
            # self.connector.land
            self.update_button("takeoff_button", "Vol terminé", "black")
        else:
            self.update_button("takeoff_button", "Drone non connecté", "red")

    def drone_connect(self):
        """Action déclenchée lors du clic sur le bouton 'Connexion'."""
        self.connector.connect()
        if self.connector.connected:
            self.update_button("connect_button", "Connecté", "green")
        else:
            self.update_button("connect_button", "Erreur de connexion", "red")

    def execute_mouvement(self):
        if self.connector.connected:
            self.current_move_index = 0 
            # self.connector.takeoff()
            print("Décollage en cours")
            timer = 2
            time.sleep(timer)
            i = 0
            self.update_movement(auto_indent = False)
            self.update_button("takeoff_button", "Vol en cours", "green")
            for coord_gate in self.coord_relat:

                gate_type = self.gate_types[i]

                x_target, y_target, z_target = coord_gate

                dist = self.calculer_distance(x_target, y_target, z_target, 0, 0, 0)

                x_middle = int((x_target) / 2)
                y_middle = int((y_target) / 2)
                z_middle = int((z_target) / 2 + int(dist / 20))

                # self.connector.drone.curve_xyz_speed(x_middle, y_middle, z_middle, x_target, y_target, z_target, 60)
                print("Curve en cours : " + str(x_middle) + " " + str(y_middle) + " " + str(z_middle) + " " + str(x_target) + " " + str(y_target) + " " + str(z_target))
                time.sleep(timer)
                self.update_movement(auto_indent = False)
                # self.connector.drone.move_forward(150)
                print("straight line en cours : 150 ")
                time.sleep(timer)
                self.update_movement(auto_indent = False)

                if gate_type == "hex":
                    # self.connector.drone.rotate_clockwise(90)
                    print("Rotation en cours : 90 ")
                    time.sleep(timer)
                elif gate_type == "hoop":
                    # self.connector.drone.rotate_counter_clockwise(90)
                    print("Rotation en cours : -90 ")
                    time.sleep(timer)
                i += 1
        else:
            return
        
    def calculer_distance(self, x1, y1, z1, x2, y2, z2):
            return round(math.sqrt((x2 - x1)**2 + (y1 - y1)**2 + (z2 - z1)**2), 2)

    def draw_mouvement_step_by_step(self):
        """Dessine les mouvements un à un, à intervalle d'une seconde."""
        self.current_move_index = 0  # Réinitialiser l'index

        # Démarrer le processus de dessin progressif
        self.update_movement()

        # for _ in range(len(self.coord_cart)):
        #     self.update_movement(auto_indent = False)

    def update_movement(self, auto_indent = True):
        """Met à jour l'affichage avec un mouvement à chaque appel."""
        if self.current_move_index < len(self.coord_cart):
            item = self.coord_cart[self.current_move_index]
            mouvement_type, points = item

            # Utiliser la même logique pour dessiner les mouvements
            ax2 = self.ax2
            if mouvement_type == "point":
                ax2.scatter(points[0][0] / 100, points[0][1] / 100, points[0][2] / 100, c='g', marker='o')
            elif mouvement_type == "straight line":
                for i in range(1, len(points)):
                    ax2.plot([points[i-1][0] / 100, points[i][0] / 100], 
                             [points[i-1][1] / 100, points[i][1] / 100], 
                             [points[i-1][2] / 100, points[i][2] / 100], c='g') 
            elif mouvement_type == "curve":
                for i in range(1, len(points)-1):
                    ax2.plot([points[i-1][0] / 100, points[i][0] / 100, points[i+1][0] / 100], 
                             [points[i-1][1] / 100, points[i][1] / 100, points[i+1][1] / 100], 
                             [points[i-1][2] / 100, points[i][2] / 100, points[i+1][2] / 100], c='g')

            # Rafraîchir l'affichage
            self.ax2.figure.canvas.draw_idle()
            root.update_idletasks() 
            root.update()

            # Avancer à l'index suivant
            self.current_move_index += 1

            if auto_indent:
                # Appeler cette méthode après 1 seconde pour le mouvement suivant
                self.master.after(1000, self.update_movement)  # 1000 ms = 1 seconde

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneApp(root)
    root.mainloop()
