<!-- socle: couche=decisions zone=publique -->
# ADR-0028 — Les messages du moteur dans la langue du projet : le message français pour clé

> statut : acceptée · date : 2026-10-14 · lu : decisions@efc2a4a3

## Contexte

Une mémoire s'écrit en anglais depuis ADR-0020@04e8d4db, mais le moteur
parle toujours français : les refus des hooks que lit l'agent, les
constats des contrôles, l'état du démarrage, la ligne de commande,
l'installeur et les textes qu'il pose dans un projet (B-0038@4a0088d1).
Environ 400 messages, la plupart des f-strings, dans 25 modules. Le code
et ses commentaires restent en français (ADR-0027@a8288770) ; ce qui doit
changer, c'est ce que le projet lit. Pas de gettext : ses catalogues se
compilent par un outil hors de la bibliothèque standard.

## Décision

- Un message reste écrit en français dans le code, enveloppé :
  `trad("le fichier {chemin} manque", chemin=rel)`. Le texte français est la
  clé du catalogue d'une autre langue (`engine/socle/messages_en.py`, un
  dictionnaire du texte français vers sa traduction). Un texte défini loin
  de son emploi (une table, une constante) se marque `a_traduire("…")` et se
  traduit à l'emploi.
- Les variables s'écrivent `{nom}` et se donnent par leur nom ; une
  accolade dont le nom n'est pas donné reste telle quelle.
- La langue des messages est celle de la mémoire (`[memory] language`) :
  la ligne de commande la pose dès qu'elle charge un projet, et la rend à
  la sortie ; l'installeur prend celle de `--language`, à défaut celle du
  projet qu'il met à jour. Pas de réglage distinct pour les messages.
- Un message absent du catalogue sort en français : rien ne casse. Un test
  lit le code et refuse un texte enveloppé absent du catalogue, une
  traduction dont les variables diffèrent, une entrée que plus rien
  n'emploie, et un message écrit en dur là où le moteur en émet.
- Ce que le moteur relit de sa propre sortie (la ligne qui nomme les
  contrôles en échec) se lit dans toutes les langues.
- Les textes en prose posés dans un projet ont un gabarit par langue,
  `<nom>.<langue>.<ext>`, comme ceux de la mémoire. Les noms des contrôles
  (`memoire.format`) sont des identifiants et ne se traduisent pas.

## Conséquences

Un projet français ne voit rien changer : le texte qu'il lit est la clé
elle-même, et ses tests gardent leurs valeurs attendues. Un projet anglais
lit le moteur en anglais. Ajouter une langue : un catalogue
`messages_<langue>.py` et ses gabarits. Le coût : chaque message nouveau
s'écrit deux fois, ce que le test exige. Pour défaire : vider le catalogue,
et tout sort de nouveau en français ; `trad` sans catalogue ne fait que
remplir les variables.
