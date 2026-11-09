<!-- socle: couche=decisions zone=publique -->
# ADR-0053 — Une citation survit à un changement des seules métadonnées de l'entrée citée

> statut : acceptée · date : 2026-11-09 · validation : D-0086@6fc022c5 · source : B-0135@b3b4bf15, ADR-0008@b1d9ee74, J-2026-11-09-U@eecea2d0 · lu : decisions@973a147d

## Contexte

Une lecture se prouve par l'empreinte de la version lue (ADR-0008). Cette
empreinte couvrait tout le texte de l'entrée, sa ligne de métadonnées
comprise : changer un statut, ce qu'une entrée attend (`après`) ou ce
qu'elle a lu périmait chaque citation neuve de cette entrée, à récrire
après une relecture qui n'apprenait rien ; et deux entrées qui se citent
avec empreinte dans leurs métadonnées se périmaient l'une l'autre à
chaque réécriture. L'agent de JustCook l'a rapporté le 8 novembre
(B-0135). Théo a validé la règle (D-0086), qui change ce qu'attend un
test.

## Décision

- L'empreinte d'une entrée couvre son titre et son corps, sans sa ligne de
  métadonnées, les lignes `>` qui suivent le titre. `socle show` l'imprime,
  `socle new` et la renumérotation la posent.
- Une citation à l'empreinte du texte entier, celle des citations écrites
  avant, reste acceptée tant qu'elle correspond, à la version actuelle ou à
  celle du commit où elle paraît : rien de la mémoire existante ne casse.
- Ce qu'une citation prouve reste ce que dit ADR-0008, pour le corps lu.
  Le statut se lit dans l'index des décisions ou du backlog, et celui
  d'une demande dans le fichier de sa réponse.
- `test_une_citation_neuve_d_une_version_perimee_est_refusee` change : la
  clôture du sujet y change aussi son corps, et la citation de la version
  d'avant reste refusée. Trois tests nouveaux montrent qu'un changement des
  seules métadonnées ne périme pas une citation neuve, qu'une citation au
  texte entier reste bonne, et que deux entrées qui se citent dans leurs
  métadonnées restent bonnes ensemble.

## Conséquences

Une citation ne prouve plus qu'un statut a été lu. L'auto-test, qui
injecte une citation périmée par un changement du corps, l'attrape
toujours. La défaire : revenir à l'empreinte du texte entier
(`empreinte_entree` dans `engine/socle/memory.py`) ; les citations d'une
forme ou de l'autre restent acceptées, par `empreintes_entree`.
