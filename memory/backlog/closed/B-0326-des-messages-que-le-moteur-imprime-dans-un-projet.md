<!-- socle: couche=backlog zone=publique -->
# B-0326 — Des messages que le moteur imprime dans un projet installé citent des identifiants de la mémoire de l'atelier : « Et maintenant » dit D-0071, un refus du hook D-0098

> statut : abandonné · origine : J-2026-11-21-K · priorité : basse · lu : backlog@81bbee84 · ref : D-0168

Relevé en faisant T-0029 (J-2026-11-21-K). ADR-0033 veut que le produit
ne renvoie jamais à l'atelier. B-0271 en traite les commentaires du
moteur ; ce sont ici des textes que l'installeur et le hook impriment
dans un projet installé, dont un identifiant de ce dépôt désigne, dans
ce projet, une autre entrée ou rien. L'étape d'approbation de « Et
maintenant » en session cloud (`et_maintenant`, dans
`engine/socle/installer.py`) dit « l'humain les lit dans la pull
request (D-0071) » ; le refus du hook de l'agent pour l'écriture d'un
fichier protégé finit par « (D-0098) ». Le catalogue anglais
(`engine/socle/messages_en.py`) compte des dizaines de lignes de la forme
« (D-…) », « (B-…) », dont une part dans des messages ; aucun test ne
garde les messages du produit comme `tests/test_notes_de_version.py`
garde les notes.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : deux messages imprimés chez un projet citent un identifiant de ce dépôt ; jamais vu gêner l'agent de chess. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] aucun message que le moteur imprime dans un projet installé ne cite un identifiant de la mémoire de l'atelier, et un test le garde
