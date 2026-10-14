<!-- socle: couche=decisions zone=publique -->
# ADR-0027 — Les noms de fichiers et les commandes du socle en anglais, son code en français

> statut : acceptée · date : 2026-10-13 · lu : decisions@a1a1eb4f · validation : D-0021

## Contexte

La décision sur les langues (ADR-0002@4252b51e) met le contenu en français
et le code en anglais, identifiants Python publics compris. Le moteur ne
l'a jamais suivie : ses dossiers, ses modules, ses gabarits, trois
commandes et six options sont en français, et ses 359 fonctions et classes
publiques aussi. Théo a signalé les noms de fichiers et de dossiers
(B-0045@b5c00d64), puis choisi le périmètre (D-0021@90ac5e5d) : ce qu'on
tape et les noms de fichiers passent en anglais, les fonctions gardent
leurs noms français.

## Décision

- En anglais : les commandes et leurs options, les clés de
  configuration, les noms de fichiers et de dossiers du socle (moteur,
  modules, gabarits, adaptateurs, banc). Les anciens noms de commandes et
  d'options restent acceptés le temps d'une version.
- En français : le contenu (documentation, mémoire, messages,
  commentaires, valeurs de statut) et les identifiants du code, fonctions,
  classes et variables. Un module s'importe sous son nom français, comme
  le reste du code qui l'emploie (`from socle import memory as memoire`).
- Les noms des fichiers de tests et de la documentation ne changent pas :
  renommer un fichier de tests ferait passer chacun de ses tests pour
  supprimé, et les liens gelés de la mémoire vers la documentation
  mourraient.
- Un chemin cité dans une couche qui ne se réécrit pas (le journal, les
  décisions, les demandes, les faits) reste valide s'il a existé dans
  l'historique du dépôt : la mémoire ne suit pas un renommage, et un
  chemin inventé, qui n'a jamais existé, reste refusé.
- Un renommage n'est ni un assouplissement ni du code nouveau : le cliquet
  laisse passer une correspondance code ↔ doc ou une valeur liée qui suit
  ses fichiers sous leur nouveau nom, et le contrôle du code testé compare
  un fichier renommé à son ancien texte. Les renommages se lisent commit
  par commit. Ce n'est pas propre à ce dépôt : tout projet renomme.

## Conséquences

Ce qu'on tape et ce qu'on voit dans l'arborescence est en anglais ; le code
se lit en français, comme le contenu. Les noms retenus : `help`, `private`
(`status`, `install`, `lock`, `extract`, `recover`, `term`, `move`),
`reviewed`, `--short`, `--yes`, `--brief`, `--repo`, `--record` ; les
dossiers `engine/`, `templates/`, `adapters/`, `bench/`. Le dossier du moteur de ce dépôt est
écrit dans son verrou, un fichier protégé : jusqu'à ce que Théo l'y
renomme, un lien `moteur` vers `engine` garde le lanceur fonctionnel. Pour
défaire : renommer en sens inverse ; les alias d'import rendent le
renommage indépendant du code. Remplace ADR-0002 sur les identifiants.
