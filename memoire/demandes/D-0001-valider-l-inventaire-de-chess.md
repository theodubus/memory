<!-- socle: couche=demandes zone=publique -->
# D-0001 — Valider l'inventaire de ce que chess contient de générique (porte du jalon 1)

> date : 2026-10-10 · bloque : rien, le travail a continué en attendant (politique, point 8)

## Décision demandée

Valider l'inventaire `docs/inventaire-chess.md`, porte du jalon 1 du cadrage,
et dire ce que désigne le « carnet de 720 Ko » du cadrage.

## Contexte

Tu as demandé les jalons 1 à 5 dans cette session, avec leurs portes humaines
mises en file. Le jalon 1 inventorie ce que le dépôt chess contient de
générique ; sa porte est ta validation. Les jalons 2 à 5 ont été construits
en s'appuyant sur cet inventaire : s'il est faux, ce qui en découle est à
relire.

L'inventaire classe chaque dispositif de chess en trois groupes : repris dans
le socle (le hook qui refuse un SHA complété de tête, l'état calculé au
démarrage, le script de vérification à code de sortie unique, le cliquet de
mutation, les tests qui confrontent la documentation au code), resté propre
à chess (la mesure de force, les deux binaires, les rustines archivées), ou
ajouté par le socle (format de mémoire, contrat des demandes, cliquet
généralisé).

Il relève aussi une divergence entre le cadrage et le dépôt. Le cadrage cite
« un carnet de 720 Ko ». Le carnet de bord de chess est privé et hors du
dépôt : je ne peux pas le mesurer. En revanche, le fichier
`chess:tools/README.md`, qui porte les mesures, les verdicts et les sections
« en vol », fait 726 061 octets.

## Éléments cités

- 689ce77 — le commit de chess lu pour l'inventaire, la fusion de la revue de documentation du 7 octobre 2026.
- `docs/inventaire-chess.md` — l'inventaire lui-même, dans ce dépôt, avec ses mesures et ses trois groupes.
- `chess:tools/README.md` — le fichier de chess qui sert de journal des mesures et des verdicts, de 9 446 lignes.

## Options

- **Valider tel quel** : effort nul ; risque faible, une pièce mal classée se
  rattrapera quand l'installeur sera essayé sur chess au jalon 8 ;
  réversible.
- **Valider avec corrections** : tu nommes ce qui est mal classé ; effort
  d'une session courte de ma part ; risque nul ; réversible.
- **Refuser** : l'inventaire est à refaire ; effort d'une session, plus la
  relecture des jalons 2 à 5 ; réversible.

## Conséquences

Si tu valides, le jalon 1 est clos et la porte disparaît de l'état dérivé.
Si tu refuses, je refais l'inventaire puis relis les jalons qui s'en servent.
Sans réponse, rien ne bloque : la demande reste en attente dans l'état
dérivé à chaque démarrage de session, et l'inventaire reste une hypothèse
de travail.

## Recommandation

Valider. Vérifié : chaque pièce citée a été lue au commit indiqué, les
tailles ont été mesurées avec `wc`, et les vérifications rapides de chess
(format, lint, tests de debug) passent dans ce conteneur en trois minutes
environ. Supposé : que le « carnet de 720 Ko » désigne `chess:tools/README.md`
— la taille concorde à 1 % près, mais je n'ai pas accès au carnet privé pour
comparer.

## Réponses possibles

- `valider` — inventaire validé ; le carnet de 720 Ko est le carnet privé, la taille du README est une coïncidence.
- `valider-readme` — inventaire validé ; le carnet de 720 Ko est `chess:tools/README.md`, à traiter comme un journal à borner.
- `corriger` — le texte de ta réponse dit ce qui est mal classé.
- `refuser` — l'inventaire est à refaire.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
