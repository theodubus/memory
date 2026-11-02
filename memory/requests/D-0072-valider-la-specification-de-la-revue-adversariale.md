<!-- socle: couche=demandes zone=publique -->
# D-0072 — Valider la spécification de la revue adversariale d'un lot (ADR-0042, B-0124)

> date : 2026-11-02

## Décision demandée

Valider la spécification de la revue adversariale d'un lot, écrite dans
ADR-0042 à partir des hypothèses que vous avez validées, avant que l'agent
en écrive le code.

## Contexte

Les contrôles du socle jugent la forme du travail d'un agent, pas son
fond : un défaut de logique, un cas qu'aucun test n'exerce, un code qui
contredit une spécification passent tous les contrôles. La revue
adversariale le fait relire, avant sa livraison, par un relecteur qui n'a
pas le contexte de l'agent et cherche à le prendre en défaut. Vous avez
validé mes hypothèses sur quand la faire, qui relit, ce qu'un constat
bloque, son coût, sa portée et ce que vous en lisez. ADR-0042 en fait une
spécification, résumée ici :
- **Quand** : avant le push qui livre un lot qui change du code, une
  spécification ou un test ; une seule passe.
- **Le moteur** : une commande nouvelle, `socle review`, imprime le
  dossier du relecteur, et rien d'autre : la consigne adversariale, le
  diff du lot (tronqué au-delà d'un plafond), les sujets qu'il ferme avec
  leur « Fait quand », et les décisions qu'ils citent.
- **L'agent** : un skill du socle nouveau, `socle-review`, posé par
  l'installeur et protégé. Sous Claude Code, l'agent lance un sous-agent
  dont le seul message est ce dossier. L'agent corrige chaque constat
  fondé et écarte les autres en une ligne ; le récap dit combien. Rien
  n'est posté sur GitHub.
- **D'abord une option, mesurée** : les instructions posées dans un projet
  ne l'exigent pas encore. Ce dépôt l'applique à ses propres lots, et le
  banc la mesure sur des défauts connus. Selon la mesure, une demande
  nouvelle vous proposera d'en faire la règle par défaut ou une option des
  questions de départ.

## Éléments cités

- ADR-0042@7da2d910 — la spécification de la revue adversariale, proposée,
  que cette demande soumet.
- D-0070@51d47c63 — vos réponses aux questions de cadrage de la revue :
  `valider`, les hypothèses de l'agent s'appliquent, « supposées ».
- B-0124@dfa9917f — le sujet de la revue adversariale, et ses deux critères
  de fin : la procédure écrite, et la mesure au banc.

## Où regarder

- [ADR-0042](https://github.com/theodubus/memory/blob/99f731ec233bffff7c5aecd45d70223853044ee6/memory/decisions/ADR-0042-la-revue-adversariale-d-un-lot-par-un-relecteur-sa.md) :
  la spécification entière. Vérifier surtout la section « Décision » : ce
  que reçoit le relecteur, et le choix d'en faire d'abord une option
  appliquée à ce seul dépôt.

## Options

- **Valider** : l'agent écrit la commande, le skill, la règle de ce dépôt,
  leurs tests et leur auto-test, puis la mesure au banc ; effort moyen,
  quelques heures, et des sessions du banc dans votre abonnement, chacune
  plafonnée à l'équivalent de 2 dollars ; risque faible, rien ne change
  pour les projets équipés avant la demande suivante ; réversible.
- **Refuser** : la revue attend, sans spécification ; effort nul ;
  risque, le fond du travail reste sans regard avant la livraison ;
  réversible.

## Conséquences

Si vous validez, ADR-0042 passe à « acceptée », et l'agent livre la revue
dans la prochaine pull request, puis vous rapporte ce que le banc en a
mesuré. Si vous refusez, ADR-0042 est rejetée et la revue attend. Sans
réponse, rien ne se code, et l'agent travaille sur autre chose.

## Recommandation

Valider. Vérifié : la spécification suit vos réponses à D-0070, et le
moteur reste sans agent (il prépare le dossier, il ne lance personne).
Supposé : que la revue trouve des défauts que les contrôles ratent, à un
coût qui le vaut ; c'est ce que le banc mesurera avant qu'elle ne
s'applique aux autres projets.

## Réponses possibles

- `valider` — ADR-0042 est acceptée ; l'agent code la revue, l'applique à ce dépôt et la mesure au banc.
- `refuser` — ADR-0042 est rejetée ; la revue attend.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
