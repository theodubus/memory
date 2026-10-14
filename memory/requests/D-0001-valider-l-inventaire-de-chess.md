<!-- socle: couche=demandes zone=publique -->
# D-0001 — Le tri de ce que chess contient de générique (repris, laissé, ajouté) est-il le bon ?

> date : 2026-10-10 · réécrite après ton retour du 10 oct. · bloque : rien, le travail a continué

## Décision demandée

Valider ou corriger le tri des dispositifs de chess entre « repris dans le
socle », « laissé à chess » et « ajouté par le socle » — c'est la porte du
jalon 1 du cadrage — et dire à quoi correspond le « carnet de 720 Ko » que
cite le cadrage.

## Contexte

Le jalon 1 du cadrage est un inventaire : avant de construire le socle,
lister ce que le dépôt chess a déjà et qui servirait à n'importe quel projet.
Sa porte est ta validation. J'ai lu chess au dernier commit de main (7 oct.)
sans rien y modifier, et j'ai écrit l'inventaire dans ce dépôt. Les jalons 2
à 5 ont été construits sur ce tri ; s'il est faux, ils sont à revoir.

Voici le tri, résumé. Le détail, pièce par pièce, est dans le fichier
indiqué plus bas.

**Repris dans le socle, généralisé.**
L'état calculé au démarrage de session (`tools/etat.sh`), qui devient la
commande `socle state`. Le hook qui refuse un SHA complété de tête, repris
tel quel. Le hook de fin de tour qui refuse de conclure sur un arbre cassé.
La trace qui prouve que les hooks ont tiré. Le script de vérification qui
exécute tout et rend un seul code de sortie (`tools/verify.sh`), qui devient
`socle verify`. Le cliquet de mutation : plafond par fichier, qui casse à la
hausse et signale la baisse, et le test qui exige chaque fichier dans le
cliquet. Les tests qui confrontent la doc au code : chaque outil nommé dans
la doc, le chiffre de bench de la doc vérifié contre le binaire. Le principe
des scripts `*-test.sh` : une branche de refus s'éprouve sur des dépôts
fabriqués, qui devient l'auto-test du socle.

**Laissé à chess, parce que propre aux échecs.** Toute la mesure de force
(SPRT, arbitres, matchs, NNUE), les deux binaires, les rustines archivées,
l'exclusion des branches de Codex. Un cas limite : le contrôle « le balayage
de mutation tourne-t-il encore », générique mais lié à l'API GitHub, mis au
backlog.

**Ajouté par le socle, absent de chess.** Le format de mémoire lisible par
script, le contrat des demandes, le cliquet sur tous les seuils, l'ajout seul
du journal, l'empreinte du moteur, le refus des copies, la correspondance
code ↔ doc qui bloque (chess ne fait que signaler), les tests creux, le test
de régression rejoué sur le commit parent.

**Le carnet de 720 Ko.** Le cadrage parle d'un « carnet de 720 Ko ». Le
carnet de bord de chess est privé, hors du dépôt : je ne peux pas le mesurer.
En revanche `tools/README.md`, qui porte dans chess les mesures, les verdicts
et les sections « en vol », fait 726 061 octets, soit environ 720 Ko. Je ne
sais donc pas lequel le cadrage désigne. Ça compte pour la suite : si c'est
`tools/README.md`, c'est un fichier du dépôt qu'il faudra traiter comme un
journal à borner quand le socle sera installé sur chess.

## Éléments cités

- `tools/etat.sh` — le script de chess qui imprime l'état du travail au démarrage de chaque session.
- `tools/verify.sh` — le script de chess qui lance toutes les vérifications et rend un seul code de sortie.
- `tools/README.md` — le fichier de chess de 9 446 lignes qui sert de journal des mesures et des verdicts.

## Où regarder

- L'inventaire complet, avec le rôle de chaque pièce et ce qu'elle devient :
  [docs/inventaire-chess.md](../../docs/inventaire-chess.md), en particulier
  ses trois sections « Générique : repris dans le socle », « Spécifique : reste
  dans chess » et « Ce que chess n'a pas et que le socle ajoute ».
- Le fichier de chess de 720 Ko environ :
  [chess, tools/README.md](https://github.com/theodubus/chess/blob/main/tools/README.md).

Ce qu'il faut vérifier : qu'aucune pièce de chess que tu tiens pour générique
n'est rangée dans « laissé à chess », qu'aucune pièce reprise ne te semble
inutile, et ce que désigne le carnet de 720 Ko.

## Options

- **Valider tel quel** : effort nul ; risque faible, une pièce mal rangée se
  verra quand le socle sera installé sur chess au jalon 8 ; réversible.
- **Corriger** : tu nommes la pièce mal rangée ; effort d'une session courte
  de ma part ; risque nul ; réversible.
- **Refuser** : l'inventaire est à refaire ; effort d'une session, plus la
  relecture des jalons 2 à 5 ; réversible.

## Conséquences

Si tu valides, le jalon 1 est clos. Si tu refuses, je refais l'inventaire puis
relis ce qui en dépend. Sans réponse, rien ne bloque : la demande reste listée
à chaque démarrage de session, et l'inventaire reste une hypothèse de
travail.

## Recommandation

Valider, en répondant à la question du carnet. Vérifié : chaque pièce citée a
été lue dans chess, les tailles mesurées, et avec l'adaptateur que j'en ai
tiré les vérifications de la CI de chess passent toutes sous le socle.
Supposé : que le carnet de 720 Ko soit `tools/README.md` — la taille
concorde à 1 % près, mais je n'ai pas accès au carnet privé.

## Réponses possibles

- `valider` — tri validé ; le carnet de 720 Ko est le carnet privé.
- `valider-readme` — tri validé ; le carnet de 720 Ko est `tools/README.md` de chess, à borner comme un journal.
- `corriger` — le texte de ta réponse dit ce qui est mal rangé.
- `refuser` — l'inventaire est à refaire.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
