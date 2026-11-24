<!-- socle: couche=backlog zone=publique -->
# T-0149 — Le bac à sable de l'outil shell mesuré dans une session locale sur une suppression hors du projet, et la couche retenue soumise à Théo avec son modèle de menace

> statut : abandonné · origine : J-2026-11-21-Q · besoin : B-0318 · lu : backlog@6c894b15 · ref : D-0168

Un commit : dans une session locale de Claude Code, qu'une session cloud n'a pas (sur l'ordinateur de Théo, s'il le prête à la session, ou par lui), ce que fait le bac à sable de l'outil shell sur la suppression d'un dossier qui contient le projet ; le relevé dans `docs/fabrication/`, à côté de `docs/fabrication/garanties-hors-du-hook.md` ; une demande, qui cite B-0318, soumet à Théo la couche retenue, avec son modèle de menace : le guide propose le bac à sable, l'installeur l'écrit dans les réglages, ou le risque est accepté et dit par le guide. Un avertissement du hook de fin de tour du socle ne s'ouvre pas : aucune preuve vue en session (ADR-0098).

T-0149 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0318, sous « X1 — ne compte que si l'agent cherche à contourner le socle » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] le relevé de la mesure est dans `docs/fabrication/`
- [ ] une demande soumet la couche et son modèle de menace à Théo, et sa réponse est consignée au journal
