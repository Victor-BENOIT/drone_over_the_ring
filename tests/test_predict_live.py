from djitellopy import Tello
from ultralytics import YOLO
import cv2

# Fonction pour calculer l'aire d'une boîte englobante (bounding box)
def calculate_area(x1, y1, x2, y2):
    return abs((x2 - x1) * (y2 - y1))

# Fonction pour calculer l'intersection sur l'union (IoU)
def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = calculate_area(*boxA)
    boxBArea = calculate_area(*boxB)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Initialiser le drone Tello
tello = Tello()
tello.connect()

# Commencez à capturer le flux vidéo du Tello
tello.streamon()

# Chargement des modèles YOLO pour les cercles et les hexagones
model_hoop_path = r'resources\runs\detect\train9\weights\last.pt'
model_hexagon_path = r'resources\runs\detect\train5\weights\last.pt'

model_hoop = YOLO(model_hoop_path)
model_hexagon = YOLO(model_hexagon_path)

# Définition du seuil de confiance pour les détections
threshold = 0.9

# Boucle principale pour traiter chaque image du flux vidéo du Tello
while True:
    frame = tello.get_frame_read().frame  # Capture de l'image du flux vidéo du Tello

    # Convertir l'image de BGR à RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    H, W, _ = frame_rgb.shape

    # Application des modèles YOLO pour les cercles et les hexagones
    results_hoop = model_hoop(frame_rgb)[0]
    results_hexagon = model_hexagon(frame_rgb)[0]

    # Stockage des hoops et hexagones pour comparaison
    hoops = []
    hexagons = []

    # Traitement des détections de cercles
    for result in results_hoop.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            hoops.append([x1, y1, x2, y2, score])

    # Traitement des détections d'hexagones
    for result in results_hexagon.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            hexagons.append([x1, y1, x2, y2, score])

    # Filtrer les hoops superposés avec les hexagones
    for hoop in hoops:
        hoop_area = calculate_area(hoop[0], hoop[1], hoop[2], hoop[3])
        keep_hoop = True
        for hexagon in hexagons:
            hexagon_area = calculate_area(hexagon[0], hexagon[1], hexagon[2], hexagon[3])
            iou = calculate_iou([hoop[0], hoop[1], hoop[2], hoop[3]], [hexagon[0], hexagon[1], hexagon[2], hexagon[3]])

            # Si l'aire est similaire à 90% et la superposition (IoU) à 90%
            if abs(hoop_area - hexagon_area) / hoop_area < 0.3 and iou >= 0.7:
                keep_hoop = False
                break

        if keep_hoop:
            # Dessine un rectangle bleu pour les cercles
            cv2.rectangle(frame_rgb, (int(hoop[0]), int(hoop[1])), (int(hoop[2]), int(hoop[3])), (255, 0, 0), 4)  # Bleu
            # Affichage du type et du score
            cv2.putText(frame_rgb, f"HOOP {hoop[4]:.2f}",
                        (int(hoop[0]), int(hoop[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.3,
                        (255, 0, 0),
                        3,
                        cv2.LINE_AA)

    # Afficher toujours les hexagones
    for hexagon in hexagons:
        # Dessine un rectangle rouge pour les hexagones
        cv2.rectangle(frame_rgb, (int(hexagon[0]), int(hexagon[1])), (int(hexagon[2]), int(hexagon[3])), (0, 0, 255), 4)  # Rouge
        # Affichage du type et du score
        cv2.putText(frame_rgb, f"HEXAGON {hexagon[4]:.2f}",
                    (int(hexagon[0]), int(hexagon[1] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (0, 0, 255),
                    3,
                    cv2.LINE_AA)

    # Affiche l'image annotée dans une fenêtre
    cv2.imshow('Détection en temps réel', frame_rgb)

    if cv2.waitKey(1) & 0xFF == 27:  # Appuyer sur 'ESC' pour quitter
        break

# Arrêtez le flux vidéo et libérez les ressources
tello.streamoff()
cv2.destroyAllWindows()
