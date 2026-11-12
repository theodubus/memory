# La consommation d'une session qui orchestre : relevé

B-0173. Relevé le 2026-11-12 sur la session d'orchestration du 9 au 12
novembre, arrêtée à 18 h 26 UTC le 12 (avant la mesure elle-même) ; le
contrôle hors échantillon court jusqu'à 18 h 46. Le relevé a été éprouvé
par une revue sans contexte, dont les onze constats sont corrigés ici.

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
- le poids de lecture **0,042**, ajusté sur les seize relevés de la
  fenêtre lus le 12 novembre entre 18 h 07 et 18 h 15 (section
  « Étalonnage »), les autres poids inchangés.

Une journée est un jour UTC. Une reprise est le premier appel après un
silence de plus de cinq minutes, ou d'une heure, dans une même
conversation. Un appel tiède relit un cache encore chaud : il suit le
précédent de moins que la durée du cache de sa conversation, et n'est pas
le premier après un compactage. Ce que le socle injecte se reconnaît dans
la transcription (sortie du hook de démarrage, relecture de son fichier
par tout outil, section du socle d'AGENTS.md, sorties des commandes,
dossiers de revue, refus des hooks), se mesure en octets, et s'estime en
jetons à 3,5 octets par jeton (hypothèse).

```sh
python3 bench/consumption.py <dossier des transcriptions> --until 2026-11-12T18:26:00Z \
    --weight-read 0.042 --point 2026-11-12T18:07:03.8Z,0.00/0.53 ...   # les seize relevés ci-dessous
python3 bench/consumption.py <dossier des transcriptions> --until 2026-11-12T18:47:00Z \
    --weight-read 0.042 --point ... --control 2026-11-12T18:46:55.6Z,0.92/0.65
```

## Les relevés de la fenêtre (donnée d'entrée)

Lus par l'orchestrateur le 12 novembre (UTC), en part de la fenêtre de
cinq heures et de la semaine. Les instants sont au dixième de seconde,
sauf 18:13:40,808 (milliseconde donnée par la revue) ; aucun appel ne
tombe à moins de 0,19 s d'un relevé ; la fin du compactage
(18:13:40,752) précède le sien de 56 ms.

| instant | fenêtre | semaine | instant | fenêtre | semaine |
| --- | ---: | ---: | --- | ---: | ---: |
| 18:07:03,8 | 0,00 | 0,53 | 18:09:21,6 | 0,49 | 0,60 |
| 18:07:25,6 | 0,39 | 0,59 | 18:09:27,5 | 0,50 | 0,60 |
| 18:07:54,1 | 0,41 | 0,59 | 18:09:52,4 | 0,51 | 0,60 |
| 18:08:11,0 | 0,43 | 0,59 | 18:10:03,5 | 0,52 | 0,60 |
| 18:08:29,1 | 0,44 | 0,59 | 18:10:09,1 | 0,53 | 0,60 |
| 18:08:36,5 | 0,45 | 0,59 | 18:13:40,808 | 0,54 | 0,61 |
| 18:08:45,9 | 0,46 | 0,60 | 18:14:37,3 | 0,59 | 0,61 |
| 18:08:58,7 | 0,48 | 0,60 | 18:15:20,8 | 0,62 | 0,62 |

Contrôle hors échantillon : 18:46:55,6, 0,92 / 0,65.

## Étalonnage : ce que vaut un point de fenêtre

Un relevé lu à un instant reflète les appels finis avant celui dont la
réponse le porte (décalage d'un appel) ; un compactage est un de ces
appels, mais la transcription ne le chiffre pas. Au poids de lecture
0,042 :

| de | à | appels | lecture de cache | écriture de cache | coût pondéré | points | jetons par point |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 18:07:03,8 | 18:07:25,6 | 1 | 58 k | 576 k | 1,17 M | 39 | 30 k |
| 18:07:25,6 | 18:07:54,1 | 1 | 634 k | 4 k | 44 k | 2 | 22 k |
| 18:07:54,1 | 18:08:11,0 | 1 | 639 k | 2 k | 45 k | 2 | 23 k |
| 18:08:11,0 | 18:10:09,1 | 9 | 5,84 M | 16 k | 314 k | 10 | 31 k |
| 18:10:09,1 | 18:13:40,808 | 1 | 657 k | 1 k | 32 k | 1 | 32 k |
| 18:13:40,808 | 18:14:37,3 | compactage | — | — | non chiffré | 5 | — |
| 18:14:37,3 | 18:15:20,8 | 1 | 58 k | 42 k | 94 k | 3 | 31 k |

Les neuf intervalles de 18:08:11 à 18:10:09 sont regroupés ici ; pris un
à un (un ou deux points chacun), ils vont de 18 000 à 40 000 jetons par
point, l'arrondi d'un relevé valant un point.

- **18 h 07 : la relecture à froid**, confirmée. Un seul appel réécrit
  576 000 jetons de cache d'une heure : 39 points de la fenêtre, 6 de la
  semaine.
- **18 h 07 à 18 h 10 : ce n'est pas le compactage.** Ce sont des appels
  ordinaires du tour, chacun relisant de 634 000 à 657 000 jetons depuis
  le cache : environ 1,2 point par appel.
- **Le compactage coûte 5 points (± 1)**, mesuré une seule fois, celui du
  12 à 18 h 13 (659 000 jetons). Le relevé de 18:13:40,808, porté par sa
  réponse, compte l'appel de 18:10:08 (1 point) ; celui de 18:14:37,3,
  porté par l'appel suivant, compte le compactage seul (5 points). L'appel
  suivant, qui réécrit le contexte neuf, en coûte 3. Le modèle de l'outil
  (relire la conversation, écrire le résumé) n'en donne que 2,1 : il
  sous-estime d'un facteur 2,4 et ne sert que de borne basse.
- **Un point de la fenêtre de cinq heures vaut environ 29 500 jetons
  pondérés** sur Fable (29 200 à 30 000 à l'arrondi des relevés près). Le
  poids de lecture qui explique le mieux les seize relevés (moindres
  carrés sur les relevés, le compactage exclu) est 0,042 ; l'arrondi admet
  0,042 à 0,044, et 0,039 à 0,047 si l'on ne garde que les relevés qui
  bornent les deux longues séquences (39 et 12 points). Le troisième
  chiffre du poids n'est donc pas sûr ; la valeur du point l'est. En
  unités directes : environ 14 700 jetons d'écriture de cache d'une heure
  (14 600 à 15 000), ou environ 700 000 jetons de lecture de cache
  (660 000 à 710 000). Une écriture d'une heure pèse 45 à 48 lectures
  (43 à 51 sur les seules longues séquences), contre 20 sous le tarif
  public : le poids 0,1 surestime les lectures de 2,4 fois.
- **Un point de la semaine vaut environ 7 points de la fenêtre** (62
  contre 9 ; de 6,1 à 7,9 à l'arrondi près).
- **Opus pèse environ 2,2 fois moins par jeton, avec une grande
  dispersion.** Douze fenêtres se sont closes sur un refus. Leur coût,
  une fois retranchés les points de Fable (à 29 500 jetons par point),
  donne pour Opus une médiane de 65 000 jetons pondérés par point sur onze
  fenêtres, mais de 13 000 à 129 000 ; la douzième, où Fable a travaillé
  seul, n'en dit rien. Les deux fenêtres où Opus a travaillé seul (le 9)
  donnent 32 000 et 96 000 ; celle du 10 à 22 h 50 rend Opus deux fois
  plus lourd que Fable par jeton. Le contrôle hors échantillon confirme la
  médiane : de 18:15:20,8 à 18:46:55,6, 28,6 points prédits (11,8 de
  Fable, 16,7 d'Opus) pour 30 relevés.

## Les journées

Coût pondéré au poids de lecture 0,042 ; les points sont estimés à 29 500
jetons par point pour Fable et 65 000 pour Opus (médiane incertaine, voir
plus haut). Le tarif public (lecture 0,1) donne les mêmes jetons et un
coût plus élevé : 35,4 M le 11, 25,6 M le 12, 109 M sur la session.

| jour | portée | modèle | conv. | appels | écriture de cache | lecture de cache | sortie | coût pondéré | points estimés |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 11 nov. | principale | Fable | 1 | 215 | 1,70 M (1 h) | 66,9 M | 383 k | 8,13 M | 276 |
| 11 nov. | sous-agents | Opus | 18 | 934 | 6,91 M (5 min) | 116,7 M | 606 k | 16,57 M | 255 |
| 12 nov. | principale | Fable | 1 | 132 | 2,53 M (1 h) | 63,4 M | 232 k | 8,89 M | 302 |
| 12 nov. | sous-agents | Opus | 11 | 582 | 3,25 M (5 min) | 68,9 M | 399 k | 8,95 M | 138 |
| 12 nov. | sous-agents | Fable | 1 | 2 | 74 k | 69 k | 5 k | 0,12 M | 4 |
| 9–12 nov. | principale | les deux | 1 | 1 018 | 8,7 M | 399 M | 1,42 M | 41,2 M | — |
| 9–12 nov. | sous-agents | les deux | 43 | 1 867 | 12,1 M | 228 M | 1,38 M | 31,6 M | — |

Par sous-agent (Opus) : un coût médian de 0,68 M le 11 et 0,54 M le 12,
soit 10 et 8 points à 65 000 jetons par point (de 7 à 21 et de 6 à 17
entre les deux fenêtres d'Opus seul) ; un maximum de 3,38 M et 1,88 M
(52 et 29 points). Au plus trois sous-agents actifs à la fois le 11, deux
le 12 (un sous-agent est actif tant que ses appels se suivent à moins de
cinq minutes). Le premier appel d'un sous-agent porte un contexte médian
de 68 000 jetons (au plus 88 000).

### Le coût d'un appel selon le contexte

Appels tièdes de Fable, coût médian complet (écriture, lecture, sortie) :

| contexte | appels | coût médian | dont lecture |
| ---: | ---: | ---: | ---: |
| 60 k à 140 k | 67 | 0,55 point | 0,16 point |
| 260 k à 340 k | 60 | 0,73 point | 0,43 point |
| 480 k à 560 k | 72 | 1,13 point | 0,74 point |

L'écriture et la sortie d'un appel ne dépendent pas de la taille du
contexte : un appel tiède coûte deux fois plus à 520 000 jetons qu'à
100 000, pas cinq.

### La taille de la conversation principale

| jour | appels | contexte médian | 90e centile | maximum | appels au-delà de 400 k |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9 nov. | 332 | 436 k | 735 k | 790 k | 188 |
| 10 nov. | 339 | 337 k | 631 k | 865 k | 122 |
| 11 nov. | 215 | 306 k | 504 k | 605 k | 60 |
| 12 nov. | 132 | 523 k | 629 k | 658 k | 108 |

Quatre compactages en quatre jours (un automatique à 902 000 jetons, trois
demandés entre 606 000 et 659 000). Un seul est mesuré : 5 points, plus 3
pour l'appel suivant. Les trois autres ne le sont pas ; leur borne basse
est de 2 à 2,2 points, leur appel suivant de 2,2 à 4,3.

### Les reprises après une pause

| jour | portée | pause de plus de | reprises | coût de ces premiers appels | part du coût de la portée | premier appel / appel médian |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 11 nov. | principale | 5 min | 36 | 3,25 M | 40 % | × 1 |
| 11 nov. | principale | 1 h | 4 | 2,30 M | 28 % | × 20 |
| 11 nov. | sous-agents | 5 min | 33 | 6,27 M | 38 % | × 19 |
| 12 nov. | principale | 5 min | 25 | 5,06 M | 57 % | × 1 |
| 12 nov. | principale | 1 h | 5 | 4,34 M | 49 % | × 34 |
| 12 nov. | sous-agents | 5 min | 16 | 2,46 M | 27 % | × 19 |
| 9–12 nov. | principale | 1 h | 15 | 11,48 M | 28 % | × 27 |
| 9–12 nov. | sous-agents | 5 min | 50 | 9,01 M | 28 % | × 19 |

La conversation principale écrit son cache pour une heure : une pause de
cinq à soixante minutes ne coûte rien de plus (le premier appel vaut
l'appel médian). Au-delà d'une heure, tout se réécrit : le 12, cinq
reprises font 49 % de la conversation principale, environ 147 points, 29
par reprise. Les sous-agents écrivent leur cache pour cinq minutes : un
sous-agent repris après sa revue, ou après toute attente de plus de cinq
minutes, réécrit tout son contexte (× 19 l'appel médian), soit plus du
quart de ce que coûtent les sous-agents.

## Ce que le socle injecte

| jour | démarrages (resume / compact) | octets reçus au démarrage | AGENTS.md, section du socle | commandes du socle (sorties) | dossiers de revue lus | relectures du hook | refus des hooks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 11 nov. | 8 / 1 | 20,5 Ko | 19 × 12,7 Ko | 214, 205 Ko, dont `show` 96 Ko | 12, 195 Ko | 0 | 6, 2,8 Ko |
| 12 nov. | 7 / 1 | 18,4 Ko | 13 × 12,7 Ko | 114, 116 Ko, dont `show` 51 Ko | 5, 144 Ko | 1, 8,8 Ko | 6, 3,1 Ko |

Les colonnes comptent la conversation principale et les sous-agents.

- **La sortie du hook de démarrage n'arrive pas entière.** `socle state`
  imprimait le 12 novembre 28 463 octets (environ 8 100 jetons) : état
  dérivé 3,0 Ko, index des décisions 7,9 Ko (70 ADR), chantier actif
  5,8 Ko, mémoire canonique 11,7 Ko. Toutes les sorties du hook de la
  session (de 25,7 à 30,2 Ko) ont dépassé le seuil de Claude Code : il les
  range dans un fichier et ne remet à l'agent qu'un aperçu d'environ
  2 Ko, l'état dérivé et le début de l'index des décisions. L'agent a
  relu ce fichier quatre fois en quatre jours, par `sed` ou `head`, sans
  règle qui le lui demande : le 9 à 14 h 39 (18,6 Ko), le 9 à 16 h 46 et
  21 h 06 (moins de 1 Ko), le 12 à 18 h 14 après le compactage (8,8 Ko).
  Les démarrages comptés par la trace locale des hooks (12 à 13 par jour)
  dépassent ceux de la transcription (8 à 9) : des reprises sans appel au
  modèle.
- **AGENTS.md** entre au démarrage de chaque conversation ; sa section du
  socle fait 12,7 Ko sur environ 16. Elle est entrée 6 fois dans la
  conversation principale (démarrage, quatre compactages, une
  modification) et une fois dans chacun des 43 sous-agents.
- **Le socle pèse peu, à quelques pour cent près.** Part moyenne du
  contexte relu qui vient du socle, et part du coût qu'on lui attribue au
  prorata :

  | portée | sans AGENTS.md (contexte / coût) | avec sa section du socle |
  | --- | ---: | ---: |
  | conversation principale | 5,0 % / 4,4 % | 5,9 % / 5,0 % |
  | sous-agents | 3,7 % / 2,5 % | 6,7 % / 4,8 % |

  Dans la conversation principale, les dossiers de revue que
  l'orchestrateur lit font 1,5 % du contexte, les sorties de `show` 1,1 %,
  les relectures du fichier du hook 0,5 %, les aperçus de démarrage 0,5 %.
  Dans les sous-agents, la section du socle d'AGENTS.md en fait 3,1 %, les
  dossiers de revue 2,3 %, les sorties de `show` 1,0 %. Une fois B-0010
  fait, la sortie du hook, bornée à 10 Ko, entrera entière dans le
  contexte à chaque démarrage, compactage et reprise : environ 2 % du
  contexte de la conversation principale au lieu de 0,5 %.
- **Le dossier de revue** se lit au début de la relecture et reste dans
  le contexte du relecteur, qui le relit depuis le cache à chacun de ses
  appels. Vingt et un sous-agents en ont reçu un (somme de leurs
  lectures) : de 3,5 à 60 Ko, médiane 23 Ko, certains lus en partie. Il
  coûte environ 19 000 jetons pondérés par relecteur sur toute sa
  relecture, soit 0,3 point d'Opus.

La borne à poser revient à B-0010 (l'état sous 10 Ko, D-0093) ; la mesure
y ajoute que la sortie du hook doit rester sous le seuil d'aperçu de
Claude Code, que la transcription ne donne pas : au-dessus, la borne ne
sert à rien, l'agent ne lit que 2 Ko.

## Ce que la mesure montre

1. Les **reprises après plus d'une heure** font le quart à la moitié de la
   conversation principale (28 % le 11, 49 % le 12) : environ 29 points
   par reprise sur une conversation de 600 000 jetons.
2. La **taille de la conversation principale** double le coût de chaque
   appel tiède entre 100 000 et 520 000 jetons (0,55 point contre 1,13 sur
   Fable) ; elle pèse surtout par les relectures à froid, qui la
   réécrivent en entier.
3. Les **sous-agents** font la moitié à deux tiers du total les jours de
   lot (50 % le 12, 67 % le 11), dont plus d'un quart en reprises après
   cinq minutes.
4. **Le modèle compte** : Fable pèse environ 2,2 fois plus qu'Opus par
   jeton pour la limite, en médiane ; selon la fenêtre, de 0,4 à 4,4 fois.
5. **Le socle pèse peu** (4 à 7 % du contexte relu selon la portée), mais
   son état de démarrage n'arrive pas entier.

## Ce que la mesure suggère pour les règles

- **Quand compacter.** Avant toute attente qui peut passer l'heure (une
  limite proche, une CI longue, une réponse de l'humain, la nuit), et à la
  fin de chaque lot. Le compactage fait sur un cache tiède coûte environ
  8 points (5 ± 1, et 3 pour l'appel suivant) ; la même conversation
  relue à froid après l'attente en coûte une quarantaine (39 mesurés à
  576 000 jetons). Après la pause, il est trop tard : compacter relit
  alors la conversation à froid. Hors attente, compacter vers 500 000
  jetons s'il reste au lot une quinzaine d'appels : l'économie, environ
  0,6 point par appel (1,13 contre 0,55), rembourse le compactage en une
  quinzaine d'appels ; à 300 000 jetons, elle n'est que de 0,2 point par
  appel, et le compactage (estimé à 7 points à cette taille) en demande
  une quarantaine.
- **Combien de sous-agents à la fois.** Le nombre ne change pas le coût
  total, mais un sous-agent coûte 8 à 10 points en médiane (de 6 à 21
  selon la valeur du point d'Opus), jusqu'à 52, et chacun réveille la
  conversation principale (1,1 point par réveil à 520 000 jetons, 0,55 à
  100 000). Deux à la fois, trois au plus ; ne pas en lancer quand la
  fenêtre a moins de 30 points devant elle : coupé par la limite, chacun
  se relirait à froid.
- **Quand reprendre un sous-agent.** Dans les cinq minutes qui suivent sa
  fin, le reprendre ne coûte que ses appels. Au-delà, son contexte se
  réécrit en entier : le reprendre ne vaut que si son contexte reste sous
  environ 70 000 jetons, ce que porte le premier appel d'un sous-agent
  neuf ; sinon, un sous-agent neuf avec la consigne et les constats, ou,
  pour quelques lignes, la conversation principale elle-même.
- **Quel modèle pour quel travail.** La conversation qui orchestre, longue
  et relue à chaque appel, sur le modèle qui pèse le moins par jeton
  (Opus, ici, en médiane) ; le modèle le plus cher pour des tâches courtes
  et bornées où sa qualité compte. À confirmer par un relevé de la fenêtre
  pendant un travail sur Opus seul : la dispersion des fenêtres ne permet
  pas mieux.
- **À l'approche d'une limite.** En dessous de 20 à 30 points restants :
  finir le pas en cours, écrire la mémoire (chantier actif, journal),
  compacter, ne lancer ni sous-agent ni attente. La reprise se fait alors
  sur une conversation courte.

### La piste de la session neuve

Un réveil qui ouvre une session neuve, lue depuis la mémoire, au lieu de
reprendre la longue :

| contexte de la conversation à la pause | relecture à froid | session neuve (estimée) |
| ---: | ---: | ---: |
| 100 k | 7 points | 5 à 10 points |
| 300 k | 20 points | 5 à 10 points |
| 650 k | 44 points | 5 à 10 points |

La relecture à froid réécrit tout le contexte (2 jetons pondérés par jeton
pour un cache d'une heure ; 39 points mesurés à 576 000 jetons). La
session neuve n'est pas mesurée : son coût est une estimation (voir
« Ce qui reste incertain »). Elle l'emporte au-delà d'environ 150 000
jetons, et ses appels suivants coûtent deux fois moins qu'à 500 000. Son
prix est ce que la mémoire ne dit pas : elle ne reprend que ce que le
chantier actif et le journal portent. Compacter avant la pause donne
presque le même gain, mais suppose de voir la pause venir ; la session
neuve sert quand la limite a coupé sans prévenir.

## Ce qui reste incertain

- Les relevés de la fenêtre sont arrondis au centième et lus par
  l'orchestrateur ; le décalage d'un appel entre usage et relevé est une
  hypothèse, que les chiffres confirment sans la prouver. Les instants
  sont donnés au dixième de seconde ; l'ordre des appels et des relevés
  n'en dépend pas (voir « Les relevés de la fenêtre »).
- Le poids de lecture n'est sûr qu'à quelques millièmes près (0,039 à
  0,047 selon les relevés retenus) ; les colonnes en jetons pondérés en dépendent, la
  valeur du point (29 200 à 30 000) beaucoup moins.
- Le seul étalonnage direct porte sur Fable. La valeur d'Opus vient de
  fenêtres closes : la première du 9 s'est ouverte à 11 h 40, avant la
  session (14 h 38), et ses 32 000 jetons par point sont donc une borne
  basse ; les fenêtres qui contiennent un compactage omettent ses quelque
  5 points ; dans la fenêtre où Fable a travaillé seul, ses appels
  n'expliquent que 79 points sur 100, compactage non compris.
- Un seul compactage est mesuré (5 points ± 1, à 659 000 jetons) ; le coût
  des autres, et celui d'un compactage à 300 000 jetons (7 points avec
  l'appel suivant, en appliquant à la borne basse le facteur mesuré), sont
  des estimations.
- La session neuve est une estimation : son premier appel coûterait 2 à
  4,5 points (le premier appel après un compactage en coûte de 2,2 à 4,3 ;
  le premier appel d'un sous-agent, s'il écrivait son cache pour une
  heure, 4,5) ; la relecture de la mémoire qui suit n'est mesurée nulle
  part, et l'hypothèse de cinq à dix appels tièdes à 0,55 point lui donne
  3 à 5,5 points.
- La part du socle attribue à ses octets une part du coût d'entrée de
  chaque appel au prorata du contexte, écriture et lecture confondues ;
  les 3,5 octets par jeton du français sont une hypothèse ; d'AGENTS.md,
  seule la section du socle est comptée.
- Le seuil au-delà duquel Claude Code range la sortie d'un hook dans un
  fichier n'est pas connu ; toutes les sorties de la session l'ont dépassé.
- Un sous-agent compte comme actif tant que ses appels se suivent à moins
  de cinq minutes : une convention, qui ne voit pas un outil long.
