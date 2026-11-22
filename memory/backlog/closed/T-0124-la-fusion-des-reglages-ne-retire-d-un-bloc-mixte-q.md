<!-- socle: couche=backlog zone=publique -->
# T-0124 — La fusion des réglages ne retire d'un bloc mixte que les commandes du socle, et l'installeur nomme celles du projet qu'il garde

> statut : fait · origine : J-2026-11-21-L · ref : J-2026-11-22-F · besoin : B-0328 · lu : backlog@cc3cfb46

Un commit : la fusion des réglages (`engine/socle/installer.py`) ne
retire d'un bloc que les commandes du socle, garde le bloc s'il lui en
reste, et les commandes gardées passent par le même signalement que
celles d'un bloc propre au projet (B-0054, T-0030) ; un correctif, avec
son test qui échoue sur le commit parent ; une note de version.

## Fait quand

- [x] un réglage dont un bloc `Stop` réunit le hook du socle et `bash tools/lint.sh` garde `bash tools/lint.sh` après l'installation et après une mise à jour, l'installeur le nomme, et un test qui échoue sur le commit parent le prouve ; de même sous `SessionStart`
