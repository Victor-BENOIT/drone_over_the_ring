import tkinter as tk
import math
from tkinter import messagebox
import ast


class Map:
    def __init__(self, largeur_canevas=900, hauteur_canevas=815, largeur_rectangle=900, hauteur_rectangle=715):
        self.largeur_canevas = largeur_canevas
        self.hauteur_canevas = hauteur_canevas
        self.largeur_rectangle = largeur_rectangle
        self.hauteur_rectangle = hauteur_rectangle
        self.parcours = False
        
        self.fenetre = tk.Tk()
        self.fenetre.title("Map")
        self.fenetre.bind("<Button-1>", self._on_click)
        
        self.centrer_fenetre()
        
        self.canvas = tk.Canvas(
            self.fenetre, width=self.largeur_canevas, height=self.hauteur_canevas, bg="white"
        )
        self.canvas.pack()
        
        self.portes = []
        
        self._setup_canvas()
        self._draw_rectangle_with_grid()
        self._draw_point_and_protractor()
        self._create_menu_bar()
        
        points_data = self._charger_donner_fichier('detectedn_doors.txt')
        self._draw_points(points_data)
        
    def _setup_canvas(self):
        self.x1 = (self.largeur_canevas - self.largeur_rectangle) // 2
        self.y1 = (self.hauteur_canevas - self.hauteur_rectangle) // 2
        self.x2 = self.x1 + self.largeur_rectangle
        self.y2 = self.y1 + self.hauteur_rectangle

    def _create_menu_bar(self):
        menu_bar = tk.Menu(self.fenetre)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.fenetre.quit)
        file_menu.add_command(label="Parcours", command=self._create_parcours)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.fenetre.config(menu=menu_bar)
        
    def _draw_rectangle_with_grid(self):
        self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="white", outline="black", width=2)
        
        for i in range(self.x1, self.x2 + 1, 50):
            self.canvas.create_line(i, self.y1, i, self.y2, fill="gray", dash=(2, 2))
            self.canvas.create_text(i, self.y1 - 10, text=str(i - self.x1), fill="black", font=("Arial", 8))
            
        for j in range(self.y1, self.y2 + 1, 50):
            self.canvas.create_line(self.x1, j, self.x2, j, fill="gray", dash=(2, 2))
            self.canvas.create_text(self.x1 - 20, j, text=str(j - self.y1), fill="black", font=("Arial", 8))
            
    def _draw_point_and_protractor(self):
        self.point_x = self.x1 + self.largeur_rectangle // 2
        self.point_y = self.y1
        
        rayon_point = 5
        
        self.canvas.create_oval(
            self.point_x - rayon_point, self.point_y - rayon_point,
            self.point_x + rayon_point, self.point_y + rayon_point,
            fill="red", outline="red"
        )
        
        rayon_rapporteur = 200
        for angle in range(0, 181, 10):
            radian = math.radians(angle)
            x_start = self.point_x + rayon_rapporteur * math.cos(radian)
            y_start = self.point_y + rayon_rapporteur * math.sin(radian)
            self.canvas.create_line(self.point_x, self.point_y, x_start, y_start, fill="gray", width=1)
            
            if angle % 30 == 0:
                self.canvas.create_text(x_start, y_start, text=str(angle), fill="black", font=("Arial", 8))
                
    def _charger_donner_fichier(self, fichier):
        point_data = []
        try:
            with open(fichier, 'r') as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if ligne:
                        try:
                            point = ast.literal_eval(ligne)
                            point_data.append(point)
                        except (SyntaxError, ValueError) as e:
                            messagebox.showerror("Erreur", f"Le format de la ligne est incorrect : {ligne}. Détails : {str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Le fichier {fichier} est introuvable.")
        return point_data
    
    def _draw_points(self, points_data):
        self.portes = []
        for point in points_data:
            distance = point['distance'] / 2
            angle_camera = point['angle camera']
            angle_porte = point['angle porte']
            porte_type = point['porte']
            
            radian = math.radians(angle_camera)
            x_nouveau = self.point_x + distance * math.cos(radian)
            y_nouveau = self.point_y + distance * math.sin(radian) 
            
            couleur_trait = "blue" if porte_type == "hoop" else "red"
            
            longueur_trait = 100
            angle_trait = math.radians(angle_porte + angle_camera - 90)
            
            x1_trait = x_nouveau - (longueur_trait / 2) * math.cos(angle_trait)
            y1_trait = y_nouveau - (longueur_trait / 2) * math.sin(angle_trait)
            x2_trait = x_nouveau + (longueur_trait / 2) * math.cos(angle_trait)
            y2_trait = y_nouveau + (longueur_trait / 2) * math.sin(angle_trait)
            
            self.canvas.create_line(x1_trait, y1_trait, x2_trait, y2_trait, fill=couleur_trait, width=2)
            
            self.portes.append({
                "porte_type": couleur_trait,
                "x1_trait": x1_trait,
                "y1_trait": y1_trait,
                "x2_trait": x2_trait,
                "y2_trait": y2_trait,
                "angle": angle_porte
            })
            
    def centrer_fenetre(self):
        """Centre la fenêtre au milieu de l'écran."""
        self.fenetre.update_idletasks()  # S'assurer que les dimensions de la fenêtre sont calculées
        largeur_ecran = self.fenetre.winfo_screenwidth()
        hauteur_ecran = self.fenetre.winfo_screenheight()

        x = (largeur_ecran // 2) - (self.largeur_canevas // 2)
        y = (hauteur_ecran // 2) - (self.hauteur_canevas // 2)
        
        self.fenetre.geometry(f"{self.largeur_canevas}x{self.hauteur_canevas}+{x}+{y}")

            
    def _on_click(self, event):
        event_x = ((event.x * 2) - (self.largeur_canevas - self.largeur_rectangle))/2
        event_y = ((event.y * 2) - (self.largeur_canevas - self.largeur_rectangle))/2
        
        print(f"clicked at x : {event_x}  & y : {event_y}")
        
        for index, porte in enumerate(self.portes):
            print(index)
            if (porte['x1_trait'] <= event.x <= porte['x2_trait'] or porte['x2_trait'] <= event.x <= porte['x1_trait']) and \
                    (porte['y1_trait'] <= event.y <= porte['y2_trait'] or porte['y2_trait'] <= event.y <= porte['y1_trait']):
                self._rotate_door(index)
                break
            
    def _rotate_door(self, index):
        self.portes[index]['angle'] = (self.portes[index]['angle'] + 90) % 360
        
        data_points = self._charger_donner_fichier('detectedn_doors.txt')
        data_points[index]['angle porte'] = self.portes[index]['angle']
        
        with open('detectedn_doors.txt','w') as file:
            for point in data_points:
                file.write(str(point) + '\n')
                
        self.canvas.delete("all")
        self._setup_canvas()
        self._draw_rectangle_with_grid()
        self._draw_point_and_protractor()
        self._draw_points(points_data=data_points)
        
    def _create_parcours(self):
        with open('parcours.txt', 'w') as file:
            for porte in self.portes:
                print(porte.get('porte_type'))
                x_centre = (porte['x1_trait'] + porte['x2_trait']) / 2
                y_centre = (porte['y1_trait'] + porte['y2_trait']) / 2
                angle = porte['angle']
                couleur = "BLEU" if porte.get('porte_type') == "blue" else "ROUGE"
                file.write(f"couleur={couleur}, x_centre={x_centre}, y_centre={y_centre}, angle={angle}, "
                        f"x1_trait={porte['x1_trait']}, y1_trait={porte['y1_trait']}, "
                        f"x2_trait={porte['x2_trait']}, y2_trait={porte['y2_trait']}\n")
                
        messagebox.showinfo('Success','fichier parcours créé/modifié !')
        
        # lancement du parcours
        self.parcours = True
        self.fenetre.quit()
        
    def _map_quit(self):
        self.parcours = True
        self.fenetre.quit
        self.fenetre.destroy()
        
    def run(self):
        self.fenetre.mainloop()


if __name__ == "__main__":
    app = Map()
    app.run()