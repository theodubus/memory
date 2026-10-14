<!-- socle: couche=backlog zone=publique -->
# B-0045 — Des noms de fichiers et de dossiers sont encore en français

> statut : fait · origine : J-2026-10-12-F · lu : backlog@19253d8c · ref : J-2026-10-14-A

Signalé par Théo, texte exact : « Certains noms fichiers/dossier de base
sont encore en français-> backlog à corriger ». La migration du format 2
(B-0032) n'a renommé que les chemins de la mémoire et de la configuration
d'un projet. Restent en français : les dossiers et modules du moteur
(`moteur/`, `modeles/`, `adaptateurs/`, `controles_*.py`, `prive.py`,
`memoire.py`…), les gabarits (`garde-fous.toml`, `politique.toml`,
`modeles/memoire/canonique.md`…), le dossier `banc/`, les marqueurs locaux
d'un projet (sous `.socle/trace/`, et la clé de déploiement du mode
compagnon), et, contre ADR-0002 qui veut les commandes en anglais, des
commandes et des options : `aide`, `prive` et ses actions, `relu`,
`--rapide`, `--court`, `--poser`, `--oui`, `--cadrage`, `--depot` — dont
quatre ajoutées par moi pour B-0034. À faire : un inventaire complet, des
noms anglais, d'anciens noms de commandes gardés le temps d'une version,
et une migration pour ce qui vit dans les projets.
