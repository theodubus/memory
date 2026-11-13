<!-- socle: couche=backlog zone=publique -->
# B-0196 — Avant que la demande d'une mise à jour soit poussée, la fin de tour refuse l'arbre par une ligne en échec pour chaque fichier protégé changé

> statut : ouvert · origine : J-2026-11-13-D · lu : backlog@8f4711b1

Relevé à la mise à jour du socle sur chess, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gêne 3).

Entre l'installation et le push de la demande qui couvre les fichiers
protégés changés, la fin de tour refuse l'arbre : 26 lignes en échec,
une par fichier, chacune avec sa commande de remise en état, environ
17 Ko de contexte relu ensuite à chaque appel. La cause est une, la
demande pas encore posée : une ligne qui le dit (« une mise à jour attend
sa demande : la poser ») suffirait, la liste restant lisible à la demande.
Une fois la demande poussée, ce n'est plus qu'un avertissement.

## Fait quand

- [ ] après une mise à jour dont la demande n'est pas posée, la fin de tour le dit en une ligne au lieu d'une ligne par fichier, et un test le montre
