<!-- socle: couche=decisions zone=publique -->
# ADR-0013 — La mémoire privée : un lecteur qui ne connaît pas l'outil, un verrou par commit

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-Y@caa0663f · lu : decisions@ea6d58e5

## Contexte

Le jalon 7 (B-0002@901e277f) demande les deux modes de mémoire privée du
cadrage, dépôt compagnon et chiffrement dans le dépôt, avec un signal
« indisponible » qui ne passe jamais en silence. Le moteur s'en tient à la
bibliothèque standard de Python, qui ne chiffre pas, et le cadrage laisse
l'outil de chiffrement à évaluer.

## Décision

- **La zone privée est memoire/prive/** dans les deux modes : même
  arborescence, mêmes contrôles, mêmes budgets que la zone publique.
- **Le moteur ne connaît pas l'outil de chiffrement.** Un fichier privé est
  lisible quand sa première ligne porte l'en-tête du socle, chiffré sinon.
  Un fichier privé lisible dans ce que git commite est une fuite ; un
  fichier privé illisible là où on le lit compte pour absent, et rend la
  mémoire privée indisponible. Tout filtre git convient (git-crypt en est
  un) ; le choix de l'outil revient à l'installation.
- **Le dépôt compagnon a un verrou commité** (.socle/prive.lock, le SHA du
  dépôt privé), écrit par une commande et jamais à la main ; l'adresse du
  dépôt privé reste hors du dépôt public, dans les secrets de la CI.
- **En CI, un constat privé est masqué**, texte et chemin : le journal d'un
  dépôt public est public.
- **Le contenu nouveau est privé par défaut** quand une mémoire privée
  existe (`socle new`, `--public` pour l'inverse).

## Conséquences

Un fichier privé abîmé (sans en-tête) passe pour chiffré : la mémoire est
alors signalée indisponible au lieu d'être jugée sur son format. Le passage
d'une entrée du privé au public, que le cadrage soumet à l'humain, n'est pas
détecté par un contrôle : c'est une règle écrite. Le gabarit du workflow de
CI gagne une étape, inerte sans verrou.

Le défaut « mémoire privée non accessible » du cadrage est désormais attrapé
par l'auto-test au lieu d'y être déclaré non couvert : la valeur attendue de
`test_chaque_defaut_est_attrape_et_chaque_temoin_passe`, dans
`tests/test_autotest.py`, change en conséquence (plus aucun cas indisponible).

Pour défaire : retirer `prive.py` du registre des contrôles ; la zone privée
redevient un dossier comme un autre.
