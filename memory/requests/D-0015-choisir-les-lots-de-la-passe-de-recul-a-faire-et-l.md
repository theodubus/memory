<!-- socle: couche=demandes zone=publique -->
# D-0015 — Choisir les lots de la passe de recul à faire, et leur ordre

> date : 2026-10-12 · lu : decisions@e56960e0

## Décision demandée

Choisir, parmi neuf lots de travail issus de la passe de recul sur le
socle, ceux que je fais, et dans quel ordre.

## Contexte

Tu m'as demandé une passe sur tout le code, avec du recul sur la technique
et sur ce que l'outil doit faire. J'ai fait relire le moteur en cinq parts,
avec des essais sur des dépôts jetables, puis relu le fonctionnement depuis
le cadrage et les rapports des bancs. Les bancs passent tous, mais la
relecture trouve une vingtaine de défauts graves. Des pertes de données :
la migration du format 1 efface les fichiers de mémoire pas encore
commités, et l'installation relancée depuis le projet efface son propre
moteur. Des contournements du hook de l'agent : sur 40 commandes essayées,
25 passent alors qu'elles devraient être refusées, dont l'écriture d'un
réglage local de Claude Code qui coupe tous ses hooks. Des fuites possibles
de la mémoire privée : un terme privé coupé en fin de ligne ou collé à un
autre mot n'est pas reconnu. Et des contrôles qui laissent passer ce qu'ils
annoncent attraper : 8 contrôles sur 33 n'ont jamais été vus échouer. Côté
fonctionnement, la garantie « seule la CI est incontournable » repose sur
une branche protégée que rien ne pose ni ne vérifie, la mutation ne tourne
nulle part, et rien n'a été éprouvé hors de ce dépôt. Deux défauts que
j'avais introduits la veille sont déjà corrigés.

## Éléments cités

- **Le relevé de la passe de recul** : le fonctionnement face aux six
  problèmes du cadrage, puis environ soixante-quinze constats techniques
  rangés par gravité, et le tableau des lots.
- **Le sujet de la passe de recul** : le sujet de backlog qui porte ta
  demande, avec ton texte exact.
- **Les deux défauts déjà corrigés** : le hook avant commit plantait dès
  qu'un fichier protégé changeait, et deux tests de l'avertissement au
  commit ne tournaient jamais.
- **Les neuf lots**, en bref :
  - L1, les pertes de données et la casse sur un vrai projet : migration,
    installation relancée depuis le projet, un CLAUDE.md existant écrasé,
    une seconde adoption qui casse les garde-fous, un sous-dossier ;
  - L2, les contournements du hook de l'agent : lire chaque commande par
    son découpage en arguments plutôt que par motifs sur le texte, faire
    refuser les commandes réservées à l'humain par elles-mêmes sous un
    agent, et poser puis vérifier la protection de la branche par défaut ;
  - L3, la mémoire privée : termes reconnus sous leurs formes courantes,
    mode chiffré, cadrage archivé en privé, écriture refusée quand la
    mémoire privée est indisponible ;
  - L4, l'auto-test : chaque contrôle et chaque refus vus échouer, un test
    qui l'exige, des témoins qui vérifient qu'un changement validé passe ;
  - L5, les contrôles qui laissent passer et les refus à tort : comparer
    les valeurs attendues par leurs littéraux, simplifier la lecture
    prouvée ; deux choix de conception, chacun avec sa décision écrite ;
  - L6, la lenteur de la fin de tour (jusqu'à cinq minutes ici) : sortir le
    banc et l'auto-test de la suite rapide, ce qui change l'adaptateur de
    ce dépôt, un fichier protégé que toi seul modifies ;
  - L7, la dette : deux fonctions trop grosses, des doublons, des textes
    périmés ;
  - R2, un workflow hebdomadaire de mutation, posé par l'installeur ;
  - R6, installer le socle sur le projet d'échecs pour de vrai, en mode
    adoption, et relever ses refus pendant une semaine.

## Où regarder

- [le relevé](https://github.com/theodubus/memory/blob/a668d4b07e84470dd0b9b0811d66f0ab24ba02ab/docs/recul.md) :
  lire « En bref », le tableau du fonctionnement et la section 3 (les
  lots, avec leur effort) ; les tableaux A à C donnent les défauts graves,
  un par ligne, avec le fichier en cause.
- [le sujet de la passe de recul](https://github.com/theodubus/memory/blob/a668d4b07e84470dd0b9b0811d66f0ab24ba02ab/memory/backlog.md#b-0041--une-passe-sur-tout-le-code-avec-du-recul-sur-la-technique-et-sur-ce-que-loutil-doit-faire) :
  vérifier que le relevé répond à ce que tu demandais.
- [les deux défauts déjà corrigés](https://github.com/theodubus/memory/blob/a668d4b07e84470dd0b9b0811d66f0ab24ba02ab/memory/journal/2026-10.md#j-2026-10-12-d--la-relecture-de-b-0041-trouve-deux-d%C3%A9fauts-dans-mes-livraisons-de-b-0034-corrig%C3%A9s) :
  ce qui a été fait sans attendre, et pourquoi.

## Options

- **La recommandation** : L1, L2, L3, puis L4, puis R6, puis L5 ; L6, R2
  et L7 ensuite. Effort important au total, plusieurs jours ; risque
  faible, chaque correctif livré avec un test qui échoue sur le code
  actuel ; réversible lot par lot.
- **Les correctifs seulement** (L1 à L4) : effort moyen ; le reste va au
  backlog ; réversible.
- **Le projet d'échecs d'abord** (R6, puis le reste selon ce qu'il
  mesure) : effort moyen ; risque de subir sur un vrai projet les pertes
  de données de L1, que je recommande de corriger avant ; réversible.
- **Ton propre choix**, par lots : effort et risque à la mesure.
- **Rien** : effort nul ; les défauts restent connus et notés.

## Conséquences

- Si tu valides la recommandation : je fais les lots dans cet ordre, en te
  rendant compte à la fin de chacun ; L6 me demandera une décision à part,
  puisqu'il change un fichier protégé, et R6 aussi, puisqu'il touche un
  autre dépôt.
- Si tu choisis toi-même : je fais les lots que ta réponse nomme, dans
  l'ordre qu'elle donne.
- Si tu refuses : chaque constat va au backlog, et je ne touche à rien.
- Sans réponse : rien ne se fait ; les constats restent dans le relevé.

## Recommandation

La recommandation ci-dessus : d'abord ce qui perd des données, ce que
l'agent peut contourner et ce qui peut fuir, puis ce qui le fait vérifier
par l'auto-test, puis la mesure sur un vrai projet avant les choix de
conception. Vérifié : les constats les plus graves ont été rejoués à la
main (la migration, l'installation relancée depuis le projet, le hook
contourné par un lanceur entre guillemets), et les deux défauts déjà
corrigés ont leur test, qui échoue sur l'ancien code. Supposé : l'effort de
chaque lot, estimé sans l'avoir fait, et que le projet d'échecs est le bon
terrain de mesure.

## Réponses possibles

- `valider` — je fais la recommandation, dans son ordre.
- `correctifs` — je fais L1 à L4, le reste va au backlog.
- `chess-d-abord` — je fais R6, puis je te propose la suite selon ce qu'il mesure.
- `choisir` — je fais les lots que ta réponse nomme, dans l'ordre qu'elle donne.
- `refuser` — chaque constat va au backlog, et je ne touche à rien.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
