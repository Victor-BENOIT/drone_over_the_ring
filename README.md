# Drone Over The Ring
Projet Industriel / Drone Over The Ring / MBDA

## Structure du projet

```
drone_project/
│
├── main.py                # Point d'entrée pour le contrôle du drone
│
├── log.txt                # Fichier d'enregistrement des differents mouvements réalisés
│
├── config/                # Fichiers de configuration
│   ├── __init__.py  
│   └── settings.py        # Paramètres du drone (vitesse, taille de la fenêtre, etc.)
│
├── drone_controller/      # Logique spécifique au drone
│   ├── __init__.py             
│   ├── drone.py           # Classe principale de contrôle du drone
│   ├── flying_modes.py    # Différents modes (Autonome, Manuel)
│   ├── keyboard_control.py# Contrôle par clavier pour le mode manuel
│   ├── movement.py        # Méthodes de mouvement (haut, bas, gauche, droite, recalibration)
│   ├── targeting.py       # Logique de ciblage (pour passer à travers des portes, suivi de visage, etc.) 
│   └── vision.py          # Traitement d'image et détection de visage
│
├── resources/             # Ressources externes (e.g., fichiers XML, classificateurs en cascade)
│   ├── runs/              # Dossier contenant les différents modèles de detection pour cercle et hexagones 
│   └── detect_profil.xml  # Fichier XML de détection de visage
│
├── tests/                 # Tests unitaires pour le projet
│   ├── test_movement.py   # Tests pour la logique de mouvement
│   ├── test_vision.py     # Tests pour le traitement de vision
│   └── test_battery.py    # Tests pour la gestion de la batterie
│
├── utils/                 # Fonctions utilitaires
│   ├── battery.py         # Gestion de la batterie
│   ├── pygame.py          # Gestion de l'écran
│   └── logging.py         # Stockage des déplacements du drone
│
└── README.md              # Documentation du projet
```
