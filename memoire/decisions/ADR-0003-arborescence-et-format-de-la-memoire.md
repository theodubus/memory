<!-- socle: couche=decisions zone=publique -->
# ADR-0003 — Arborescence du socle et format de la mémoire

> statut : proposée · date : 2026-10-10 · source : J-2026-10-10-B

## Contexte

Le cadrage donne des noms indicatifs et laisse l'arborescence exacte ouverte.
Elle doit être fixée avant la première installation hors de ce dépôt : une
fois des projets installés, la changer exige une migration scriptée.

## Décision

- `.socle/` porte le moteur immuable (dans un projet, sous .socle/moteur/socle/), son lanceur
  (`.socle/socle`), son verrou (`.socle/moteur.lock`), la politique, les
  garde-fous, l'adaptateur et les hooks git ; `.socle/trace/` n'est pas
  versionné.
- `memoire/` porte les cinq couches et la file des demandes : un fichier par
  couche durable, un fichier par mois de journal, un fichier par décision et
  par demande, la réponse humaine à côté de sa demande en `.reponse.toml`.
- Une entrée est un titre `## <ID> — <titre>` suivi d'une ligne `> clé :
  valeur · clé : valeur`. Identifiants `F-`, `B-`, `ADR-`, `D-` à quatre
  chiffres, `J-` daté ; préfixe `P` dans la zone privée.
- La spécification complète vit dans le moteur, `moteur/socle/FORMAT.md`,
  pour voyager avec lui dans chaque projet.

## Conséquences

Un projet installé lit le format dans .socle/moteur/socle/FORMAT.md, à la
version de son moteur. Tant qu'aucun projet n'est installé, la défaire ne
coûte qu'une réécriture du moteur et de ses tests ; après, une migration.
D'où le statut « proposée » et la demande de validation avant le jalon 8.
