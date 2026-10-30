"""Tests du moteur. Le paquet `socle` vit sous `engine/` : on l'y cherche,
pour que `python3 -m unittest discover -s tests -t .` marche sans réglage.

Les variables d'une session de Claude Code (`CLAUDECODE`,
`CLAUDE_CODE_SESSION_ID`…) se retirent : lancée par un agent, la suite doit
juger comme en CI, et un test qui veut une session d'agent la pose lui-même
(B-0060). La configuration git de la machine ne compte pas non plus."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
for _variable in [v for v in os.environ if v.startswith("CLAUDE")]:
    del os.environ[_variable]
# Ni la configuration git de la machine ni celle du système : la CI de
# GitHub n'a pas d'identité git, et un test qui en dépendait passait ici et
# échouait là-bas (J-2026-10-30-F).
os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
