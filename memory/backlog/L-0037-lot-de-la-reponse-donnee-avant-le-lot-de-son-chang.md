<!-- socle: couche=backlog zone=publique -->
# L-0037 — Lot de la réponse donnée avant le lot de son changement

> statut : en cours · origine : J-2026-11-24-AZ · après : L-0036, T-0179 · lu : backlog@d9e561c7

B-0347, au jalon JA-0005 (D-0180) : sa conception n'est pas tranchée,
sa spécification se soumet à Théo avant son code (T-0179), puis la
tâche qui l'applique s'ouvre sur sa réponse. Sorti de L-0036 à
l'écriture (J-2026-11-24-AZ).

## Revues

### Passe 1 — 2026-11-25

Commits : d6b20247..7924359c

- Bloquant : la référence de la piste B, l'ancêtre commun avec le commit de la réponse, n'épuisait aucune validation fusionnée (110 tests rouverts) ; bornée par la tâche ouverte qui la cite, et le parent du commit de la demande
- Bloquant : le modèle de menace taisait le stock des validations passées ; mesuré et dit
- Bloquant : la piste A disait à tort qu'un lot s'arrêterait en route
- Ouvre : rien

### Passe 2 — 2026-11-25

Commits : 7924359c..3d88bcf0

- Bloquant : les deux conditions jugées au seul point de départ ne couvraient plus une réponse poussée plus tôt dans la même pull request (le cas de B-0142) ; une validation ajoutée sur la branche depuis ce point couvre comme une validation de la plage
- Ouvre : rien
