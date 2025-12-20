import os
import sys
import json

# Obtenir le chemin absolu du dossier contenant ce fichier (ex: app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(BASE_DIR)
# Ajouter le dossier parent au sys.path (optionnel si tu veux importer depuis le projet)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Exemple : construire un chemin vers un fichier de config
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config','config.json')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'templates')


with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)
    #print(CONFIG)
