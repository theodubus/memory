<!-- socle: couche=demandes zone=publique -->
# D-0085 — Choisir ce que la mise à jour du socle rafraîchit dans les adaptateurs d'un projet

> date : 2026-11-09

## Décision demandée

Choisir ce qu'une mise à jour du socle fait des copies d'adaptateurs qu'un
projet possède déjà : n'en rafraîchir aucune et signaler celles qui
diffèrent, rafraîchir seulement celles des langages autres que le
principal, ou les rafraîchir toutes.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA, et qui vérifie ce que
l'agent produit. JustCook, votre application de cuisine, en est le pilote.

**Le chantier.** Le 8 novembre, vous avez validé qu'un projet écrit en
plusieurs langages ait un adaptateur par langage ; c'est livré et fusionné
ce 9 novembre. Un adaptateur est un fichier de réglages qui apprend au
socle à juger les tests d'un langage. Le socle en maintient dix, et un
projet en reçoit une copie protégée, qui ne change qu'avec votre accord.
La copie principale est `.socle/adapter.toml`, les autres vont dans un
dossier à part, .socle/adapters. Reste à préparer une version du socle, puis la
mise à jour de JustCook, qui recevra une copie de l'adaptateur Kotlin à
côté de celle de Python.

**La question.** La spécification que vous avez validée dit deux choses
qui ne s'accordent pas, et j'ai tranché seul ; la revue de mon travail l'a
relevé. Je vous la soumets avant la version.

Le point 6 de la spécification dit : « La mise à jour rafraîchit chaque
copie d'un adaptateur maintenu, que vous approuvez comme tout fichier
protégé. » Le point 7 dit : « Un projet à un seul langage ne change rien. »
Aujourd'hui, une mise à jour garde toujours la copie principale telle
quelle : la rafraîchir changerait les projets à un seul langage. J'ai donc
choisi de ne rafraîchir que les copies des autres langages ; c'est ce que
fait le code fusionné.

Deux faits pèsent contre tout rafraîchissement :

- **Une copie s'adapte au projet.** La spécification des adaptateurs le
  prévoit : un projet ajoute ses étapes propres à sa copie, nomme ses
  modules quand son code n'est pas sous `src/`, et un projet Android, comme
  JustCook, y change les commandes de Gradle (`testDebugUnitTest` au lieu
  de `test`). Rafraîchir une copie la remet à l'identique de l'adaptateur
  maintenu : l'adaptation est perdue à chaque mise à jour, et se refait par
  une demande.
- **Une copie se resserre.** Le point 2 dit qu'un fichier que deux
  adaptateurs réclament se règle en resserrant les motifs de chemins d'une
  copie, par une demande. Rafraîchie, la copie perd ce resserrement, et le
  contrôle qui refuse un fichier réclamé deux fois redevient rouge.

Ce que rafraîchir apporte : les corrections d'un adaptateur maintenu,
comme les dix que la revue a faites à l'adaptateur Kotlin ce matin, arrivent
au projet à chaque mise à jour, sans demande. Sans rafraîchissement,
l'installeur dit, à chaque mise à jour, quelle copie diffère de
l'adaptateur maintenu, et l'agent du projet vous propose par une demande
d'y reporter les corrections, en gardant ses adaptations.

Pour la première mise à jour de JustCook, les trois options posent de même
la copie Kotlin, qu'il n'a pas encore ; elles diffèrent pour sa copie
Python sous la troisième, et pour toutes les mises à jour suivantes.

## Éléments cités

Les numéros : D- une demande, ADR- une décision du projet, J- une entrée du
journal, B- un sujet du backlog ; après @, l'empreinte de la version que
j'ai lue.

- D-0083@054ce997 — votre validation de la spécification des adaptateurs
  multiples, dont les points 2, 6 et 7 sont cités plus haut.
- ADR-0051@96428594 — la décision qui recopie cette spécification dans le
  registre du projet ; votre réponse ici la modifiera par une décision
  nouvelle.
- J-2026-11-09-H@94a255f0 — le compte rendu de la revue de mon travail, dont
  le constat 10 relève que j'avais tranché seul.
- B-0095@65dbe4c6 — le sujet ouvert le 30 octobre : un projet à deux
  langages n'avait qu'un adaptateur.

## Où regarder

- [D-0083](https://github.com/theodubus/memory/blob/88596a8253fe73a6676f0cc3fbcff4325c0bd679/memory/requests/D-0083-valider-la-specification-des-adaptateurs-multiples.md) :
  les points 2, 6 et 7, pour vérifier qu'ils sont cités fidèlement.
- [La spécification des adaptateurs](https://github.com/theodubus/memory/blob/88596a8253fe73a6676f0cc3fbcff4325c0bd679/engine/socle/adapters/README.md) :
  la section « Un projet en plusieurs langages », ce que la mise à jour
  fait aujourd'hui ; la section « Kotlin », sa dernière phrase, qui dit
  qu'un projet Android adapte les commandes dans sa copie.

## Options

- **N'en rafraîchir aucune** (`valider`, recommandée) : une mise à jour pose
  les copies qui manquent, garde les autres, et dit celles qui diffèrent
  de l'adaptateur maintenu. Effort : quelques lignes et un test. Risque :
  une copie qui vieillit si personne ne donne suite au constat. Réversible.
- **Ne rafraîchir que les copies des autres langages**
  (`autres-langages`) : ce que fait le code fusionné. Effort nul. Risque :
  la copie Kotlin de JustCook, adaptée à Android, est remise à l'identique
  à chaque mise à jour. Réversible.
- **Tout rafraîchir, la copie principale comprise** (`tout-rafraichir`) :
  le point 6 au pied de la lettre. Effort : quelques lignes et un test.
  Risque : toute copie adaptée, même celle d'un projet à un seul langage,
  est remise à l'identique à chaque mise à jour, ce que le point 7
  excluait. Réversible.

## Conséquences

Si vous validez, aucune copie ne se rafraîchit plus : j'écris une
décision qui remplace le point 6 d'ADR-0051, puis le code et son test,
avant la version du socle. Si vous choisissez une autre option, de même
avec elle. Si vous refusez, en disant quoi changer, je corrige et vous soumets
le texte nouveau. Sans réponse, le code fusionné reste tel quel, et je ne
prépare pas la version qui mettrait JustCook à jour.

## Recommandation

N'en rafraîchir aucune. Vérifié : la spécification des adaptateurs prévoit
qu'un projet adapte sa copie, et la section Kotlin qu'un projet Android y
change ses commandes ; l'installeur garde déjà la copie principale à la
mise à jour. Supposé : que l'agent d'un projet donne suite, par une
demande, au constat d'une copie qui diffère.

## Réponses possibles

- `valider` — aucune copie ne se rafraîchit ; la mise à jour dit celles qui diffèrent.
- `autres-langages` — seules les copies des autres langages se rafraîchissent, comme le code fusionné.
- `tout-rafraichir` — toutes les copies se rafraîchissent, la principale comprise.
- `refuser` — l'agent corrige ce que la réponse dit, et soumet une demande nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
