import tkinter as tk
import math
from tkinter import messagebox  # Importer le module pour les boîtes de dialogue
import ast  # Utilisé pour évaluer des chaînes en tant que dictionnaire Python

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Map")

# Dimensions de la fenêtre et du rectangle (divisées par 2)
largeur_canevas = 600
hauteur_canevas = 500
largeur_rectangle = 500
hauteur_rectangle = 416

# Création du canevas
canvas = tk.Canvas(fenetre, width=largeur_canevas, height=hauteur_canevas, bg="white")
canvas.pack()

# Coordonnées pour centrer le rectangle
x1 = (largeur_canevas - largeur_rectangle) // 2
y1 = (hauteur_canevas - hauteur_rectangle) // 2
x2 = x1 + largeur_rectangle
y2 = y1 + hauteur_rectangle

# Dessiner un rectangle blanc avec un contour noir
rectangle = canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=2)

# Ajouter un quadrillage tous les 50 pixels à l'intérieur du rectangle
for i in range(x1, x2 + 1, 50):  # Lignes verticales dans le rectangle
    canvas.create_line(i, y1, i, y2, fill="gray", dash=(2, 2))
    canvas.create_text(i, y1 - 10, text=str((i - x1) * 2), fill="black", font=("Arial", 8))  # Abscisses x2

for j in range(y1, y2 + 1, 50):  # Lignes horizontales dans le rectangle
    canvas.create_line(x1, j, x2, j, fill="gray", dash=(2, 2))
    canvas.create_text(x1 - 20, j, text=str((j - y1) * 2), fill="black", font=("Arial", 8))  # Ordonnées x2

# Calcul des coordonnées du point (au milieu du haut du rectangle)
point_x = x1 + largeur_rectangle // 2  # x = milieu du rectangle
point_y = y1  # Haut du rectangle

# Dessiner le point (représenté comme un petit cercle pour la visibilité)
rayon_point = 5
canvas.create_oval(
    point_x - rayon_point, point_y - rayon_point,  # Coin supérieur gauche du cercle
    point_x + rayon_point, point_y + rayon_point,  # Coin inférieur droit du cercle
    fill="red", outline="red"  # Couleur rouge pour le point
)

# Tracer un rapporteur centré au milieu du haut du rectangle
rayon_rapporteur = 200  # Rayon du rapporteur

# Tracer l'arc du rapporteur (orienté vers le bas)
for angle in range(0, 181, 10):  # Tracer tous les 10 degrés de 0 à 180
    # Convertir l'angle en radians
    radian = math.radians(angle)
    
    # Calculer les coordonnées de la ligne du rapporteur
    x_start = point_x + rayon_rapporteur * math.cos(radian)
    y_start = point_y + rayon_rapporteur * math.sin(radian)
    
    # Dessiner la ligne
    canvas.create_line(point_x, point_y, x_start, y_start, fill="gray", width=1)
    
    # Marquer les angles tous les 30 degrés
    if angle % 30 == 0:
        canvas.create_text(x_start, y_start, text=str(angle), fill="black", font=("Arial", 8))

# Fonction pour charger les données depuis le fichier detect_door.txt
def charger_donnees_fichier(fichier):
    points_data = []
    try:
        with open(fichier, 'r') as f:
            for ligne in f:
                ligne = ligne.strip()  # Nettoyer la ligne
                if ligne:  # Vérifier que la ligne n'est pas vide
                    try:
                        point = ast.literal_eval(ligne)  # Évaluer la ligne
                        points_data.append(point)
                    except (SyntaxError, ValueError) as e:
                        messagebox.showerror("Erreur", f"Le format de la ligne est incorrect : {ligne}. Détails : {str(e)}")
    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Le fichier {fichier} est introuvable.")
    return points_data

# Charger les points à partir du fichier
points_data = charger_donnees_fichier("detected_doors.txt")

# Liste pour stocker les résultats au format demandé
portes = []

# Tracer chaque point en fonction des données
for point in points_data:
    distance = point['distance'] / 2
    angle_camera = point['angle camera']
    angle_porte = point['angle porte']
    porte_type = point['porte']
    
    # Convertir l'angle caméra en radians
    radian = math.radians(angle_camera)
    
    # Calculer les coordonnées du point en fonction de l'angle et de la distance
    x_nouveau = point_x + distance * math.cos(radian)
    y_nouveau = point_y + distance * math.sin(radian)
    
    # Calculer les coordonnées du plan (x_plan et y_plan) en entiers
    x_plan = int(x_nouveau * 2 - (largeur_canevas - largeur_rectangle))
    y_plan = int(y_nouveau * 2 - (hauteur_canevas - hauteur_rectangle))
    
    # Déterminer la couleur en fonction du type de porte
    couleur = "BLEU" if porte_type == 'hoop' else "ROUGE"
    
    # Calculer les coordonnées des extrémités du trait
    longueur_trait = 20  # Longueur totale du trait
    # Calcul de l'angle trait coloré (parallèle ou perpendiculaire)
    # Calcul de l'angle du trait coloré en fonction de l'angle de la caméra et de l'angle de la porte
    angle_trait = math.radians(angle_camera + angle_porte - 90)

    # Calculer les coordonnées des extrémités du trait coloré
    x1_trait = x_nouveau - (longueur_trait / 2) * math.cos(angle_trait)
    y1_trait = y_nouveau - (longueur_trait / 2) * math.sin(angle_trait)
    x2_trait = x_nouveau + (longueur_trait / 2) * math.cos(angle_trait)
    y2_trait = y_nouveau + (longueur_trait / 2) * math.sin(angle_trait)
    
    # Vérifier si les extrémités du trait sont dans le rectangle
    if not (x1 <= x1_trait <= x2 and y1 <= y1_trait <= y2 and
            x1 <= x2_trait <= x2 and y1 <= y2_trait <= y2):
        messagebox.showerror("Erreur", f"Le trait sort du rectangle pour le point ({x_nouveau:.2f}, {y_nouveau:.2f}) !")
    else:
        # Couleur du trait selon le type de porte
        couleur_trait = "blue" if porte_type == 'hoop' else "orange"
        
        # Dessiner le trait
        canvas.create_line(x1_trait, y1_trait, x2_trait, y2_trait, fill=couleur_trait, width=2)
        
        # Ajouter la porte à la liste
        portes.append({
            "couleur": couleur,
            "x1": int((x1_trait + x2_trait) / 2 * 2 - (largeur_canevas - largeur_rectangle)),
            "y1": int((y1_trait + y2_trait) / 2 * 2 - (hauteur_canevas - hauteur_rectangle)),
            "angle": round(math.degrees(angle_porte), 2)
        })

# Afficher les résultats dans le format demandé
print("portes = [")
for porte in portes:
    print(f"    Porte({porte['couleur']}, x1={porte['x1']}, y1={porte['y1']}, angle={porte['angle']}),")
print("]")



# Lancement de la boucle principale
fenetre.mainloop()
