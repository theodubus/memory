<!-- socle: couche=backlog zone=publique -->
# B-0120 — Les spécifications d'un projet et leurs cas d'essai : le socle ne sait pas où ils sont

> statut : en cours · origine : J-2026-11-01-G · lu : backlog@4cc6e0f8

L'agent du pilote écrit ses spécifications dans docs/specs, chacune
avec un fichier de cas d'essai (`*.cas.json`). C'est leur place, mais le
socle ne le sait pas :
- par défaut, seules les décisions comptent pour spécification
  (`[tests] spec_paths`) : une spécification que l'humain change dans
  docs/specs n'autorise pas à changer les valeurs attendues des tests
  qu'elle nomme ;
- si les tests du pilote lisent leurs valeurs attendues dans les
  `*.cas.json`, en changer une échappe à `tests.attendus`, qui ne lit que
  les fichiers de test. Supposé : à vérifier sur le pilote.

À faire, une fois vérifié : les instructions disent où vivent les
spécifications et de les déclarer (`spec_paths`, ce qui assouplit et
passe par une demande ; `[[docmap]]` du code vers elles) ; et
`tests.attendus` surveille les fichiers de données qu'un test lit pour
ses valeurs attendues.

Le 1er novembre, le pilote répond (J-2026-11-01-I). Aucun de ses tests ne
lit encore de valeur attendue dans ses fichiers de cas ; mais leurs 111
sorties attendues seront rejouées par le domaine, et rien ne protège
aujourd'hui leurs changements. Et des spécifications ont reçu leur code
sans être soumises à Théo. Ce que le socle peut faire :
- protéger les fichiers de cas que le projet déclare : ajouter un cas est
  libre, changer ou retirer un cas existant exige une demande validée,
  comme une valeur attendue dans un test ;
- signaler dans ce qui revient à l'humain une spécification qu'aucune
  demande validée n'a approuvée.

D-0066, `socle` (J-2026-11-01-L).

## Fait quand

- [ ] un projet déclare ses fichiers de cas ; changer ou retirer un cas existant exige une demande validée qui cite le fichier, et un défaut injecté l'éprouve
- [ ] l'état signale une spécification déclarée qu'aucune demande ne cite
- [ ] les instructions, le format et le guide le disent
