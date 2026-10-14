"""Tests du moteur. Le paquet `socle` vit sous `moteur/` : on l'y cherche,
pour que `python3 -m unittest discover -s tests -t .` marche sans réglage."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
