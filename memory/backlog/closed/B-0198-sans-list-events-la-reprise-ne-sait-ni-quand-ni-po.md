<!-- socle: couche=backlog zone=publique -->
# B-0198 — Sans list_events, la reprise ne sait ni quand ni pourquoi la session a été coupée

> statut : fait · ref : J-2026-11-23-G · origine : J-2026-11-13-D · priorité : basse · lu : backlog@b0542257

Relevé à la mise à jour du socle sur chess, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gêne 8).

Dans une session sans l'outil `list_events`, le skill `socle-resume`
arme ses réveils à leur borne (B-0181) : il a bien repris seul la session
de chess à 2 h 46, heure de Paris. Mais ni l'heure de la coupure ni sa
cause ne se lisent : la vérification du réveil ne peut pas dire si le
tour d'avant a fini sur une limite. Coût : 4 à 6 appels par tour qui
agit. Chercher une autre source (la transcription locale, la trace des
hooks) qui dise l'heure et la cause.

## Satisfait quand

- [x] sans `list_events`, la reprise après une limite sait si le tour d'avant a fini sur une limite, ou le tient pour inconnaissable et agit en conséquence
