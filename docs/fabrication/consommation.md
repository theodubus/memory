# La consommation d'une session qui orchestre : relevé

B-0173. Relevé le 2026-11-12 sur la session d'orchestration du 9 au 12
novembre, arrêtée à 18 h 26 UTC le 12 (avant la mesure elle-même).

## La question

Une session qui orchestre des sous-agents a vidé plusieurs fenêtres de cinq
heures par jour, et la reprise après une limite en a pris d'un coup près de
la moitié. Ce qui pèse : la conversation principale, les sous-agents, les
reprises après une pause, les compactages, ou ce que le socle injecte ?

## La méthode

L'outil [`bench/consumption.py`](../../bench/consumption.py) lit les
transcriptions de Claude Code (la conversation principale et ses
sous-agents), compte chaque appel au modèle une fois, et n'en garde que
l'usage : entrée non cachée, écriture de cache (cinq minutes ou une heure),
lecture de cache, sortie. Le coût pondéré ramène ces catégories à de
l'entrée non cachée. Deux jeux de poids :

- l'hypothèse du tarif public : lecture 0,1 ; écriture 1,25 (cinq minutes)
  ou 2 (une heure) ; sortie 5 ;
- le poids de lecture **0,047**, ajusté sur sept relevés de la fenêtre de
  cinq heures lus le 12 novembre entre 18 h 07 et 18 h 15 (section
  « Étalonnage »), les autres poids inchangés.

Une journée est un jour UTC. Une reprise est le premier appel après un
silence de plus de cinq minutes, ou d'une heure, dans une même
conversation. Ce que le socle injecte est mesuré en octets dans la
transcription, et estimé en jetons à 3,5 octets par jeton (hypothèse).

```sh
python3 bench/consumption.py <dossier des transcriptions> --until 2026-11-12T18:26:00Z \
    --day 2026-11-12 --weight-read 0.047 --point 2026-11-12T18:07:03Z,0.00 ...
```

## Étalonnage : ce que vaut un point de fenêtre

Un relevé lu à un instant reflète les appels finis avant celui dont la
réponse le porte (décalage d'un appel). Sous ce décalage, les relevés
s'expliquent ainsi (poids de lecture 0,047) :

| de | à | appels | lecture de cache | écriture de cache | coût pondéré | points | jetons par point |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 18:07:03 | 18:07:25 | 1 | 58 k | 576 k | 1,17 M | 39 | 30 k |
| 18:07:25 | 18:07:54 | 1 | 634 k | 4 k | 47 k | 2 | 23 k |
| 18:07:54 | 18:10:09 | 10 | 6,47 M | 18 k | 392 k | 12 | 33 k |
| 18:10:09 | 18:14:37 | 1 + compactage | 1,32 M | 1 k | 100 k (estimé) | 6 | — |
| 18:14:37 | 18:15:20 | 1 | 58 k | 42 k | 95 k | 3 | 32 k |

- **18 h 07 : la relecture à froid**, confirmée. Un seul appel réécrit
  576 000 jetons de cache d'une heure : 39 points de la fenêtre, 6 de la
  semaine.
- **18 h 07 à 18 h 10 : ce n'est pas le compactage.** Ce sont dix appels
  ordinaires du tour, chacun relisant de 638 000 à 657 000 jetons depuis le
  cache : 12 points, environ 1,2 point par appel. Le compactage commence
  vers 18 h 11 min 45 s (il dure 115 s et se termine à 18 h 13 min 40 s) ;
  il paraît dans le relevé de 18 h 14 min 37 s, pour 4 points environ.
- **Un point de la fenêtre de cinq heures vaut environ 29 000 jetons
  pondérés** sur Fable (de 23 000 à 33 000 selon l'intervalle). En unités
  directes : environ 15 000 jetons d'écriture de cache d'une heure
  (14 400 à 15 200, les relevés étant arrondis au centième), ou environ
  720 000 jetons de lecture de cache (de 650 000 à 800 000). Une écriture
  d'une heure pèse donc 40 à 50 fois une lecture, contre 20 sous le tarif
  public : le poids de lecture 0,1 surestime les lectures du double.
- **Un point de la semaine vaut environ 7 points de la fenêtre** (62 contre
  9 sur la séquence ; de 6,2 à 7,6).
- **Opus pèse environ 2,5 fois moins par jeton.** Douze fenêtres se sont
  closes sur un refus ; leur coût, réparti entre les modèles en prenant
  29 000 jetons par point pour Fable, donne pour Opus une médiane de
  70 000 jetons pondérés par point (de 60 000 à 130 000). Estimation
  grossière : une fenêtre peut avoir été entamée hors de cette session.

## Les journées

Coût pondéré au poids de lecture 0,047 ; les points sont estimés à 29 000
jetons par point pour Fable et 70 000 pour Opus. Le tarif public (lecture
0,1) donne les mêmes jetons et un coût plus élevé : 35,4 M le 11, 25,6 M le
12, 109 M sur la session.

| jour | portée | modèle | conv. | appels | écriture de cache | lecture de cache | sortie | coût pondéré | points estimés |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 11 nov. | principale | Fable | 1 | 215 | 1,70 M (1 h) | 66,9 M | 383 k | 8,47 M | 290 |
| 11 nov. | sous-agents | Opus | 18 | 934 | 6,91 M (5 min) | 116,7 M | 606 k | 17,16 M | 245 |
| 12 nov. | principale | Fable | 1 | 132 | 2,53 M (1 h) | 63,4 M | 232 k | 9,21 M | 318 |
| 12 nov. | sous-agents | Opus | 11 | 582 | 3,25 M (5 min) | 68,9 M | 399 k | 9,29 M | 133 |
| 12 nov. | sous-agents | Fable | 1 | 2 | 74 k | 69 k | 5 k | 0,12 M | 4 |
| 9–12 nov. | principale | les deux | 1 | 1 018 | 8,7 M | 399 M | 1,42 M | 43,2 M | — |
| 9–12 nov. | sous-agents | les deux | 43 | 1 867 | 12,1 M | 228 M | 1,38 M | 32,8 M | — |

Par sous-agent (Opus) : un coût médian de 0,70 M le 11 et 0,56 M le 12
(10 et 8 points), un maximum de 3,47 M et 1,96 M (50 et 28 points). Au
plus quatre sous-agents à la fois, les deux jours. Le premier appel d'un
sous-agent porte un contexte médian de 68 000 jetons (au plus 88 000).

### La taille de la conversation principale

| jour | appels | contexte médian | 90e centile | maximum | appels au-delà de 400 k |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9 nov. | 332 | 436 k | 735 k | 790 k | 188 |
| 10 nov. | 339 | 337 k | 631 k | 865 k | 122 |
| 11 nov. | 215 | 306 k | 504 k | 605 k | 60 |
| 12 nov. | 132 | 523 k | 629 k | 658 k | 108 |

Quatre compactages en quatre jours (un automatique à 902 000 jetons, trois
demandés entre 606 000 et 659 000). Chacun coûte environ 4 points, et
l'appel suivant 3.

### Les reprises après une pause

| jour | portée | pause de plus de | reprises | coût de ces premiers appels | part du coût de la portée | premier appel / appel médian |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 11 nov. | principale | 5 min | 36 | 3,31 M | 39 % | × 1 |
| 11 nov. | principale | 1 h | 4 | 2,30 M | 27 % | × 19 |
| 11 nov. | sous-agents | 5 min | 33 | 6,28 M | 37 % | × 18 |
| 12 nov. | principale | 5 min | 25 | 5,11 M | 55 % | × 1 |
| 12 nov. | principale | 1 h | 5 | 4,35 M | 47 % | × 31 |
| 12 nov. | sous-agents | 5 min | 16 | 2,46 M | 26 % | × 17 |
| 9–12 nov. | principale | 1 h | 15 | 11,48 M | 27 % | × 25 |
| 9–12 nov. | sous-agents | 5 min | 50 | 9,01 M | 28 % | × 18 |

La conversation principale écrit son cache pour une heure : une pause de
cinq à soixante minutes ne coûte rien de plus (le premier appel vaut
l'appel médian). Au-delà d'une heure, tout se réécrit : le 12, cinq
reprises font 47 % de la conversation principale, environ 150 points, 30
par reprise. Les sous-agents écrivent leur cache pour cinq minutes : un
sous-agent repris après sa revue, ou après toute attente de plus de cinq
minutes, réécrit tout son contexte (× 17 à × 18 l'appel médian), soit plus
du quart de ce que coûtent les sous-agents.

## Ce que le socle injecte

| jour | démarrages (resume / compact) | octets reçus par l'agent | commandes du socle (sorties) | refus des hooks |
| --- | --- | ---: | ---: | ---: |
| 11 nov. | 8 / 1 | 20,5 Ko | 215 commandes, 205 Ko, dont `show` 96 Ko | 6 refus avant outil, 2,8 Ko |
| 12 nov. | 7 / 1 | 18,4 Ko | 114 commandes, 116 Ko, dont `show` 51 Ko | 6 refus avant outil, 3,1 Ko |

Les commandes comptent la conversation principale et les sous-agents.

- **La sortie du hook de démarrage ne parvient pas à l'agent.**
  `socle state` imprime aujourd'hui 28 463 octets (environ 8 100 jetons) :
  état dérivé 3,0 Ko, index des décisions 7,9 Ko (70 ADR), chantier actif
  5,8 Ko, mémoire canonique 11,7 Ko. Toutes les sorties du hook de la
  session (de 24 à 28 Ko) ont dépassé le seuil de Claude Code : il les
  range dans un fichier et ne remet à l'agent qu'un aperçu de 2 Ko,
  l'état dérivé et le début de l'index des décisions. L'agent n'a jamais
  relu ce fichier. Les démarrages comptés par la trace locale des hooks
  (12 à 13 par jour) dépassent ceux de la transcription (8 à 9) : des
  reprises sans appel au modèle.
- **Le socle ne pèse pas dans le total.** Tout ce qu'il a mis dans la
  conversation principale (aperçus de démarrage, sorties de ses commandes,
  refus) fait en moyenne 3 % du contexte relu, soit 3 % du coût. Les
  messages des hooks sont de l'ordre du kilo-octet par jour.
- **Un dossier de revue** (`socle review --base origin/main`, pour un lot de
  256 lignes) fait 18 Ko, environ 5 000 jetons, lus une fois par un
  relecteur neuf : moins d'un point.

La borne à poser revient à B-0010 (l'état sous 10 Ko, D-0093) ; la mesure
y ajoute que la sortie du hook doit rester sous le seuil d'aperçu de
Claude Code, que la transcription ne donne pas : au-dessus, la borne ne
sert à rien, l'agent ne lit que 2 Ko.

## Ce que la mesure montre

1. Ce qui pèse est la **taille de la conversation principale**, relue à
   chaque appel : à 520 000 jetons, chaque appel coûte près d'un point de
   la fenêtre sur Fable, même tiède ; à 100 000, un sixième de point.
2. Les **reprises après plus d'une heure** font le quart à la moitié de la
   conversation principale : environ 30 points par reprise sur une
   conversation de 600 000 jetons.
3. Les **sous-agents** font la moitié à deux tiers du total les jours de
   lot, dont plus d'un quart en reprises après cinq minutes.
4. **Le modèle compte** : Fable pèse environ 2,5 fois plus qu'Opus par jeton
   pour la limite (estimation grossière).
5. **Le socle ne pèse pas** (3 %), mais son état de démarrage n'est pas lu.

## Ce que la mesure suggère pour les règles

- **Quand compacter.** Avant toute attente qui peut passer l'heure (une
  limite proche, une CI longue, une réponse de l'humain, la nuit), et à la
  fin de chaque lot. Le compactage fait sur un cache tiède coûte environ
  7 points (lui et l'appel suivant) ; la même conversation relue à froid
  après l'attente en coûte 40. Après la pause, il est trop tard : compacter
  relit alors la conversation à froid. Hors attente, compacter dès 300 000
  jetons : l'économie, environ 0,4 point par appel, rembourse le compactage
  (5 points à cette taille) en une douzaine d'appels.
- **Combien de sous-agents à la fois.** Le nombre ne change pas le coût
  total, mais un sous-agent coûte 8 à 10 points en médiane, jusqu'à 50, et
  chacun réveille la conversation principale (près d'un point par réveil à
  500 000 jetons). Deux à la fois, trois au plus ; ne pas en lancer quand
  la fenêtre a moins de 30 points devant elle : coupé par la limite, chacun
  se relirait à froid.
- **Quand reprendre un sous-agent.** Dans les cinq minutes qui suivent sa
  fin, le reprendre ne coûte que ses appels. Au-delà, son contexte se
  réécrit en entier : le reprendre ne vaut que si son contexte reste sous
  environ 70 000 jetons, ce que coûte un sous-agent neuf ; sinon, un
  sous-agent neuf avec la consigne et les constats, ou, pour quelques
  lignes, la conversation principale elle-même.
- **Quel modèle pour quel travail.** La conversation qui orchestre, longue
  et relue à chaque appel, sur le modèle qui pèse le moins par jeton
  (Opus, ici) ; le modèle le plus cher pour des tâches courtes et bornées
  où sa qualité compte. À confirmer par un relevé de la fenêtre pendant un
  travail sur Opus seul.
- **À l'approche d'une limite.** En dessous de 20 à 30 points restants :
  finir le pas en cours, écrire la mémoire (chantier actif, journal),
  compacter, ne lancer ni sous-agent ni attente. La reprise se fait alors
  sur une conversation courte.

### La piste de la session neuve

Un réveil qui ouvre une session neuve, lue depuis la mémoire, au lieu de
reprendre la longue :

| contexte de la conversation à la pause | relecture à froid | session neuve |
| ---: | ---: | ---: |
| 100 k | 7 points | 5 à 7 points |
| 300 k | 21 points | 5 à 7 points |
| 650 k | 45 points | 5 à 7 points |

La relecture à froid réécrit tout le contexte (2 jetons pondérés par jeton
pour un cache d'une heure). Une session neuve paie son premier contexte,
environ 60 000 jetons, comme un sous-agent neuf (3 points), puis la lecture
de la mémoire qu'elle reprend (2 à 4 points). Elle l'emporte dès que la
conversation dépasse environ 100 000 jetons, et ses appels suivants coûtent
cinq fois moins qu'à 500 000 jetons. Son prix est ce que la mémoire ne dit
pas : elle ne reprend que ce que le chantier actif et le journal portent.
Compacter avant la pause donne presque le même gain, mais suppose de voir
la pause venir ; la session neuve sert quand la limite a coupé sans
prévenir.

## Ce qui reste incertain

- Les relevés de la fenêtre sont arrondis au centième et lus par
  l'orchestrateur ; le décalage d'un appel entre usage et relevé est une
  hypothèse, que les chiffres confirment sans la prouver.
- Le seul étalonnage direct porte sur Fable ; la valeur d'Opus vient de
  fenêtres closes qui ont pu être entamées hors de cette session.
- L'appel qui compacte n'est pas dans la transcription : son coût (environ
  4 points) est déduit des relevés.
- Les 3,5 octets par jeton du français sont une hypothèse.
- Le seuil au-delà duquel Claude Code range la sortie d'un hook dans un
  fichier n'est pas connu ; toutes les sorties de la session l'ont dépassé.
