<!-- socle: couche=backlog zone=publique -->
# B-0318 — Hors de l'environnement cloud, rien d'autre que le hook ne borne la suppression d'un dossier qui contient le projet, ni ne fait pousser le travail à la fin de chaque réponse

> statut : ouvert · origine : J-2026-11-20-AO · ref : B-0262, T-0023, D-0120 · lu : backlog@689e597f

Le relevé de T-0023 (`docs/fabrication/garanties-hors-du-hook.md`) :
en session cloud, deux couches qui ne lisent pas le shell rattrapent la
suppression du projet et celle d'un dossier qui le contient. Le hook de
fin de tour de l'environnement refuse de conclure tant qu'un changement
n'est pas commité et poussé : la suppression ne perd que le travail du
tour. Le conteneur est jetable et ne contient que le clone : supprimer
un dossier au-dessus du projet n'y perd rien de plus. Ni l'une ni
l'autre n'existe dans une session locale de Claude Code (supposé : la
première vient des réglages du lanceur cloud, la seconde de son
conteneur) : un `rm -rf` qui vise un dossier parent du projet, sous une
forme que le hook de l'agent ne lit pas (D-0120), y perd le travail non
poussé et des fichiers de l'humain hors du projet, et rien ne le
rattrape.

Pistes, à trancher : le guide propose, pour une session locale, le bac
à sable de l'outil shell de Claude Code (les écritures bornées au dossier
du projet), ou l'installeur l'écrit dans `.claude/settings.json` ; le
hook de fin de tour du socle avertit d'un commit non poussé, comme celui
de l'environnement cloud. D'abord, mesurer dans une session locale ce
que fait le bac à sable sur une suppression hors du projet.

## Satisfait quand

- [ ] dans une session locale d'un projet équipé, la suppression d'un dossier qui contient le projet est bornée par une couche qui ne lit pas le shell, ou ce risque est accepté et le guide le dit
