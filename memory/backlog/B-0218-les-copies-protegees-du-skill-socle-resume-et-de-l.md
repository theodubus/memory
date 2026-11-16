<!-- socle: couche=backlog zone=publique -->
# B-0218 — Les copies protégées du skill socle-resume et de la CI du socle de ce dépôt en retard sur leurs gabarits, et rien ne le dit

> statut : ouvert · origine : J-2026-11-14-F · lu : backlog@df5d4436

Relancé dans le mode du verrou pour appliquer D-0110, l'installeur a
changé, au-delà de la copie qu'elle couvre, la copie protégée du skill
`socle-resume` (en retard depuis B-0181) et le workflow
`.github/workflows/socle.yml` (sans `branches-ignore: ["proto/**"]` ni
`tags`, les branches jetables). Ces changements ont été remis à leur
état du dernier commit (J-2026-11-14-F). Ce dépôt, premier utilisateur
du socle, ne tourne donc pas sur ce que le produit installe, et aucun
contrôle ni l'état ne le disent : le retard ne se voit qu'en relançant
l'installeur. Voisins : B-0214 (la section du socle d'AGENTS.md) et
B-0216 (la copie de `socle-request`).

Pistes : en mode amont, l'état ou un contrôle signale une copie protégée
différente de son gabarit ; le rafraîchissement de toutes les copies en
retard sur une seule demande, une fois B-0214 et B-0216 faits.

La revue de B-0212 (J-2026-11-14-H), constat 8 : B-0212 change le gabarit
du skill `socle-review`, que D-0110 venait de recopier ; la copie protégée
est de nouveau en retard. Tout changement d'un gabarit crée ce retard.

## Satisfait quand

- [ ] le « Fait quand » de T-0009 est tenu
