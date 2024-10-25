# drone_over_the_ring
Projet Industriel / Drone Over The Ring / MBDA

drone_project/
│
├── main.py           # Entry point for the drone control
│
│
├── config/                # Configuration files
│   ├── __init__.py  
│   └── settings.py        # Drone settings (speed, window size, etc.)
│
│
├── drone_controller/           # Drone-specific logic
│   ├── __init__.py             
│   ├── drone.py                # Core drone control class
│   ├── flying_modes.py         # Different modes (Autonomous, Manual)
│   ├── keyboard_control.py     # Keyboard listening for manual mode
│   ├── movement.py             # Movement-related methods (up, down, left, right, recalibration)
│   ├── targeting.py            # Targeting logic (for flying through doors, face following, etc.) 
│   └── vision.py               # Image processing and face detection logic
│
│
├── resources/             # External resources (e.g., XML files, cascade classifiers)
│   └── detect_profil.xml  # Face detection XML file
│
│
├── tests/                 # Unit tests for your project
│   ├── test_movement.py   # Tests for movement logic
│   ├── test_vision.py     # Tests for vision processing
│   └── test_battery.py    # Tests for battery handling
│
│
├── utils/                  # Utility functions
│   ├── battery.py          # Battery management
│   ├── pygame.py           # Screen management
│   └── logging.py          # Stockage des deplacements du drone
│
│
└── README.md              # Project documentation

