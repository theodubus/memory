<!-- socle: couche=demandes zone=publique -->
# D-0002 — Valider l'arborescence du socle et le format de la mémoire avant toute installation ailleurs

> date : 2026-10-10 · bloque : l'installation sur chess ou un autre projet (jalon 8)

## Décision demandée

Accepter, refuser ou amender la décision ADR-0003 : où vivent les fichiers du
socle dans un projet, et comment s'écrit une entrée de mémoire.

## Contexte

Le cadrage laisse ouvertes l'arborescence exacte et la forme des fichiers. Je
les ai fixées pour construire les jalons 2 à 5, en statut « proposée » :
tant qu'aucun projet n'a le socle, en changer ne coûte qu'une réécriture du
moteur ; après la première installation hors de ce dépôt, il faudra une
migration scriptée. La question vient donc maintenant, avant le jalon 8.

Ce qui est proposé, en résumé : un répertoire caché `.socle/` pour le moteur
copié, son lanceur, son verrou, la politique, les garde-fous, l'adaptateur et
les hooks git ; un répertoire `memoire/` visible pour les cinq couches et la
file des demandes. Une entrée de mémoire est un titre qui commence par son
identifiant, suivi d'une ligne de métadonnées « clé : valeur » séparées par
des points médians. La file des demandes est le répertoire
`memoire/demandes/`, et non un fichier unique `PENDING.md` comme l'évoquait
le cadrage : un fichier par demande permet de geler celles qui ont une
réponse, et l'état dérivé liste celles qui attendent.

## Éléments cités

- ADR-0003 — la décision proposée sur l'arborescence et le format, avec ses conséquences, dans `memoire/decisions/`.
- `moteur/socle/FORMAT.md` — la spécification complète du format, celle que lit le code et qui voyage dans chaque projet.

## Options

- **Accepter** : effort nul ; risque faible, le format a déjà servi à écrire
  la mémoire de ce dépôt et passe tous les contrôles ; réversible par
  migration après la première installation.
- **Amender** : tu dis quoi changer (noms de répertoires, séparateur, forme
  des identifiants, fichier unique pour la file) ; effort d'une session pour
  le moteur, ses tests et la mémoire de ce dépôt ; risque nul ; réversible.
- **Refuser** : on repart d'une autre proposition ; effort de deux sessions ;
  réversible.

## Conséquences

Si tu valides, ADR-0003 passe à « acceptée » et le jalon 8 peut installer le
socle ailleurs. Si tu refuses ou amendes, je réécris le moteur et la mémoire
de ce dépôt avant toute installation. Sans réponse, rien n'est installé hors
de ce dépôt : le jalon 8 attend, le reste avance.

## Recommandation

Accepter. Vérifié : la mémoire de ce dépôt est écrite dans ce format et
passe tous les contrôles, et l'auto-test injecte ses défauts dans un projet
installé selon cette arborescence. Supposé : qu'un répertoire caché pour
le moteur te convienne mieux qu'un répertoire visible — c'est un goût, pas
une mesure.

## Réponses possibles

- `valider` — ADR-0003 est acceptée telle quelle.
- `amender` — le texte de ta réponse dit quoi changer ; j'écris une décision qui remplace celle-ci.
- `refuser` — je propose une autre arborescence.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
