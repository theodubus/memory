<!-- socle: couche=decisions zone=publique -->
# ADR-0010 — Les liens donnés à l'humain sont des permaliens vérifiés

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-R@ab4a3756 · lu : decisions@574104cc

## Contexte

L'humain lit les messages de l'agent dans la conversation ou sur GitHub, pas
dans le conteneur de l'agent. Deux chemins écrits entre accents graves, mais
tronqués, sont devenus dans son client des liens qui menaient à un 404 ; un
troisième, juste, ouvrait la copie du conteneur au lieu de GitHub. La mémoire
vérifiait déjà chacune de ses références ; rien ne vérifiait les messages
adressés à l'humain, alors que ADR-0007@ac16270e et ADR-0009@d6de6f29 y
mettent ce qu'il doit lire et décider.

## Décision

- **`socle url <chemin|ID>`** donne le permalien d'un fichier ou d'une
  entrée de mémoire : l'adresse du dépôt, le commit poussé de la branche
  courante (pas son nom, la branche disparaît à la fusion), le chemin, et
  l'ancre du titre pour une entrée parmi d'autres. Rien n'est donné pour ce
  qui n'est pas poussé ; une version locale différente est signalée.
- **Le hook de fin de tour lit les liens du dernier message**, que l'agent
  ait agi ou non, et bloque une fois quand il trouve un lien relatif, un
  chemin entre accents graves qui n'existe pas dans le dépôt, une URL du
  dépôt vers un fichier ou un commit absents de la version poussée, ou une
  demande en attente citée sans le lien vers son fichier.
- L'état dérivé donne le lien de chaque demande en attente.
- L'adresse du dépôt se déduit de `origin` ; un relais local n'en dit rien,
  et l'humain la règle alors dans la politique (`[human] repo_url`).

## Conséquences

Un chemin d'un autre dépôt s'écrit `depot:chemin` (`chess:CLAUDE.md`), ce
que le contrôle ne prend pas pour un chemin d'ici. Les URL ont la forme de
GitHub ; un autre hébergeur demanderait de la rendre réglable. La forme des
ancres reproduit celle de GitHub sans avoir pu être comparée à son rendu :
une ancre fausse mène en haut du bon fichier, pas à un 404.

Pour défaire : retirer l'appel à `liens.problemes` du hook de fin de tour ;
`socle url` reste un outil sans effet sur les contrôles.
