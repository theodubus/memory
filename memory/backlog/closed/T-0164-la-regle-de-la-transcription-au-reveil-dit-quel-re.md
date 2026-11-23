<!-- socle: couche=backlog zone=publique -->
# T-0164 — La règle de la transcription au réveil dit quel refus marque la coupure, ce qu'est un message tapé et quoi faire d'une transcription sans le tour d'avant, et son test la prouve

> statut : fait · ref : J-2026-11-23-O · origine : J-2026-11-23-G · besoin : B-0336 · lu : backlog@77363de8

Un commit : le gabarit de `socle-resume`, en français et en anglais, sous
son budget ; la coupure est le premier `quotaLimits` après le dernier
travail de l'agent, et tout `user` tapé ensuite compte, même suivi d'un
autre refus ; un message tapé se reconnaît à son champ, mesuré sur une
transcription réelle ; une transcription sans le tour d'avant vaut
absence de transcription ; le test vérifie ces relations, et que le champ
cité est celui de la fixture `_limite` de `tests/test_consommation.py` ;
une note de version.

## Fait quand

- [x] le gabarit et son anglais disent ces trois cas, et un test échoue si la règle dit « qui précèdent », « le plus ancien », ou cite un champ que `socle consumption` ne lit pas
