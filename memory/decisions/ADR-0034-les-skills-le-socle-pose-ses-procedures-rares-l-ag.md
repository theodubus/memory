<!-- socle: couche=decisions zone=publique -->
# ADR-0034 — Les skills : le socle pose ses procédures rares, l'agent écrit celles du projet, deux contrôles les jugent

> statut : acceptée · date : 2026-10-22 · source : D-0042@1434de97 · lu : decisions@2a93e7ab

## Contexte

Théo a demandé que l'agent ajoute des skills de lui-même quand c'est
nécessaire (B-0066@2e58f27d). Un skill est une procédure rangée dans un dossier, avec
un fichier `SKILL.md` dont l'en-tête donne un nom et une description ;
l'agent ne le charge que lorsque sa description correspond à la tâche. Les
instructions du socle, elles, se relisent en entier à chaque session, et
une partie n'y sert que rarement. BMAD Method n'écrit pas de skills de
lui-même ; son module BMad Builder en fabrique sur demande, hors de l'endroit
où l'agent les charge. Théo a validé l'option 1 de D-0042.

## Décision

- **Le socle pose ses procédures rares en skills** : `socle-request` (poser
  une demande, relayer une réponse, consigner une décision en séance) et
  `socle-private-memory` (la mémoire privée), dans `.claude/skills/`, dans
  la langue de la mémoire. L'installeur les remplace à chaque mise à jour,
  comme les hooks ; la politique d'un projet neuf les protège. Les
  instructions gardent les règles et renvoient au skill par son nom ; un
  autre agent lit le fichier à ce chemin. Les refus qui s'y rapportent
  nomment le skill.
- **Leurs noms sont en anglais**, comme les noms de fichiers (ADR-0027@a8288770) :
  D-0042 les nommait `socle-demande` et `socle-memoire-privee` pour
  l'exemple.
- **L'agent écrit un skill du projet** la deuxième fois qu'il refait une
  même procédure, librement, avec une entrée au journal, sans les préfixes
  `socle-` ni `bmad-`.
- **Deux contrôles** les jugent, aux trois étages : `skills.contrat` (le nom
  est celui du dossier ; la description dit, en au moins douze mots, ce que
  fait le skill et quand s'en servir ; `socle-` reste au socle) et
  `skills.commandes` (chaque bloc de code du shell est jugé par la même
  fonction que le hook de l'agent, `hooks.refus_bash`). Une commande citée
  dans le texte n'est pas jugée : c'est ainsi qu'un skill dit ce qu'il ne
  faut pas lancer. La taille a son plafond dans les budgets des garde-fous.

## Conséquences

- Les instructions du gabarit passent de 11,4 Ko à 10,5 Ko : moins que les
  3 Ko supposés dans D-0042, parce que le tableau « Ce qui tourne tout
  seul » reste (un test exige qu'il nomme le balayage de mutation) et que
  la règle des skills du projet s'ajoute.
- La règle de la deuxième fois ne se contrôle pas : aucun script ne
  reconnaît une procédure refaite ; le journal la rend visible.
- Un skill nommé `bmad-*`, dans un projet qui déclare BMAD tiers, échappe à
  tous les contrôles (ADR-0031@ded211d6) : les instructions l'interdisent, aucun
  contrôle ne le voit.
- Dans ce dépôt, la politique est celle de Théo : la protection des skills
  du socle y attend son geste.
- Défaire : retirer les gabarits et l'étape de l'installeur, remettre les
  deux procédures dans les instructions, retirer les deux contrôles et
  leurs défauts injectés.
