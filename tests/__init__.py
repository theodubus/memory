"""Tests du moteur. Le paquet `socle` vit sous `engine/` : on l'y cherche,
pour que `python3 -m unittest discover -s tests -t .` marche sans réglage.

Les variables d'une session de Claude Code (`CLAUDECODE`,
`CLAUDE_CODE_SESSION_ID`…) se retirent : lancée par un agent, la suite doit
juger comme en CI, et un test qui veut une session d'agent la pose lui-même
(B-0060)."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
for _variable in [v for v in os.environ if v.startswith("CLAUDE")]:
    del os.environ[_variable]
