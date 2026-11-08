<!-- socle: couche=demandes zone=publique -->
# D-0082 — Choisir comment le socle juge un projet à plusieurs langages, comme JustCook en Kotlin et en Python, et où s'écrit l'adaptateur Kotlin (B-0095)

> date : 2026-11-08

## Décision demandée

Choisir comment le socle juge un projet écrit en plusieurs langages, comme
JustCook, dont l'app sera en Kotlin et les outils sont en Python ; et qui
écrit l'adaptateur Kotlin dont il a besoin. Répondez dans la conversation
par l'un des mots de la fin.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
sous forme de « demandes », des fichiers comme celui-ci, les décisions qui
vous reviennent. JustCook, votre projet d'application de cuisine, en est
le pilote : le premier projet réel équipé, qui remonte ce qui le gêne.

**Le chantier.** Le socle juge le code d'un projet par un adaptateur : un
fichier qui dit, pour un langage, où sont les sources et les tests,
comment reconnaître un test, une assertion ou une fonction publique,
comment lancer les tests et mesurer la mutation (la part des défauts
injectés dans le code que les tests attrapent). Le socle en maintient dix,
chacun éprouvé ici, par le banc des adaptateurs, un programme qui le fait
tourner sur un petit projet avec ses vrais outils. Un projet en copie un
dans son dépôt, qu'il peut retoucher, et n'en lit qu'un : ce qu'il ne lit
pas n'est pas jugé.

**La question.** JustCook a deux outils Python finis et couverts, et son
app sera en Kotlin, avec Gradle. Son agent a demandé, le 8 novembre, un
adaptateur Kotlin et un socle à plusieurs adaptateurs. Vous l'avez
renvoyé à son rôle : « je l'ai informé du fait qu'il était le pilote du
socle et lui ai demandé de faire un message expliquant sa demande et une
proposition » ; vous n'avez pas dit de préférence. Sa propre demande, dans
JustCook, attend la vôtre ; changer le moteur est coûteux à défaire.

**Les mots.** La CI : la vérification que GitHub lance à chaque envoi de
code. L'auto-test : les défauts que le socle s'injecte pour prouver que
ses contrôles les attrapent. Une valeur attendue : ce qu'un test exige du
code ; la changer demande votre accord. Le contrôle des correctifs : un
commit qui corrige un défaut doit apporter un test qui échoue sans lui.
Ce conteneur : la machine où je travaille. Les deux sessions : la mienne,
ici, et celle de l'agent de JustCook.

**Ce que le pilote a montré.** Sur une branche d'essai, du Kotlin passe la
CI sans qu'aucune règle des tests le lise : ni un test sans assertion, ni
une valeur attendue changée, ni une fonction publique sans test, ni la
mutation. Sur une autre, un prototype en Dart, le langage de Flutter, que
JustCook a comparé à Kotlin avant de le choisir, un correctif fait échouer
la CI : le contrôle des correctifs exige un test Python, le seul qu'il
sache lire. Ce défaut se corrige à part, quelle que soit votre réponse.

**Les deux voies.**
- *Plusieurs adaptateurs* : chacun déclare les chemins qu'il couvre (les
  outils Python sous `src` et `tests`, l'app sous ses modules Gradle, les
  parties de l'app) ; chaque contrôle juge un fichier par l'adaptateur qui
  couvre son chemin ; la vérification lance les tests de tous ; la
  mutation se mesure, avec ses seuils, par adaptateur. Un projet à un seul
  langage ne change rien, et les dix adaptateurs restent tels quels. Le
  moteur lit aujourd'hui un seul adaptateur, à une trentaine d'endroits :
  quelques jours de travail, sous les tests et l'auto-test, puis une mise
  à jour de JustCook, qu'une demande de JustCook vous fait approuver.
- *Un seul adaptateur* : JustCook copie l'adaptateur Kotlin dans son dépôt
  et ajoute à sa commande de tests celle de Python. Rien ne change dans le
  moteur, mais les outils Python ne sont plus jugés que par leurs propres
  tests : ni assertions vérifiées, ni fonctions nommées par un test, ni
  mutation.

**L'adaptateur Kotlin.** Il faut dans les deux voies un adaptateur Kotlin
pour Gradle : les tests sous `src/commonTest/kotlin`, `src/test/kotlin`
ou `src/androidUnitTest/kotlin` ; un test marqué `@Test`, un test
désactivé marqué `@Ignore` ou `@Disabled`, que le socle signale ; les
assertions de kotlin.test et de JUnit ; tout public sauf `private` et
`internal` ; la mutation par PIT, l'outil de mutation de Java et Kotlin.
L'agent du pilote propose de l'écrire, puisqu'il a l'app pour l'éprouver.
Je propose de l'écrire ici : Gradle et Java sont dans ce conteneur, et un
adaptateur maintenu s'éprouve ici, par le banc ; le pilote l'éprouve
ensuite sur son app. Il peut s'écrire dès votre réponse, sans attendre le
moteur ; si les chemins ne suffisaient pas à départager deux adaptateurs,
la spécification vous proposerait une autre règle.

**La demande de JustCook** a trois options : 1, un adaptateur Kotlin
propre au projet qui lance aussi Python ; 2, un socle à plusieurs
adaptateurs ; 3, réécrire les outils Python en Kotlin.

## Éléments cités

Les numéros : B- un sujet du backlog, J- une entrée du journal, datée,
suivie de sa lettre dans la journée ; après @, l'empreinte de la version
que j'ai lue. La demande de JustCook, je ne la lis pas d'ici : seul son
lien est donné plus bas, et son contenu vient du message de son agent.

- B-0095@65dbe4c6 — le sujet ouvert le 30 octobre : un projet à deux
  langages n'a qu'un adaptateur, à trancher quand le pilote fixerait sa
  pile.
- J-2026-11-08-S@b8e4e7e4 — le retour du pilote, résumé, avec votre
  message.
- B-0138@2592a463 — le correctif en Dart mal jugé, à corriger à part.

## Où regarder

- [La demande de JustCook sur les deux langages](https://github.com/theodubus/JustCook/blob/1dc97a71af70043e0eba485cbb6f493e6179ac61/memory/requests/D-0036-choisir-comment-le-socle-teste-un-depot-a-deux-lan.md) :
  à répondre une fois celle-ci tranchée.

## Options

- **Plusieurs adaptateurs, l'adaptateur Kotlin écrit ici** (`valider`,
  recommandée) : effort pour vous, valider la spécification puis la mise à
  jour de JustCook ; risque, une régression des contrôles, que les tests
  et l'auto-test bornent ; réversible, mais coûteux.
- **Plusieurs adaptateurs, l'adaptateur écrit par le pilote**
  (`kotlin-par-le-pilote`) : il l'écrit sur son app, je l'éprouve ici ;
  effort, un aller et retour de plus entre les deux sessions ; risque, un
  adaptateur pensé pour un seul projet ; réversible, mais coûteux.
- **Un seul adaptateur** (`un-adaptateur`) : j'écris l'adaptateur Kotlin
  ici, JustCook le copie et y ajoute Python ; effort, une mise à jour de
  JustCook ; risque, les outils Python moins jugés ; réversible.

## Conséquences

Avec `valider` ou `kotlin-par-le-pilote`, vous répondez à la demande de
JustCook par son option 2 ; j'écris la spécification des adaptateurs
multiples et vous la soumets avant son code. Avec `un-adaptateur`, son
option 1. Si vous refusez, le socle n'écrit aucun adaptateur Kotlin, et
JustCook choisit seul. Sans réponse, rien ne s'écrit, et JustCook attend.

## Recommandation

Plusieurs adaptateurs, l'adaptateur Kotlin écrit ici. Vérifié : le moteur
ne lit qu'un adaptateur ; du Kotlin passe la CI de JustCook sans être
jugé ; Gradle et Java tournent ici. Supposé : que les chemins suffisent à
départager les adaptateurs, ce que JustCook, ses langages séparés par
dossier, éprouvera.

## Réponses possibles

- `valider` — le socle gère plusieurs adaptateurs ; l'adaptateur Kotlin s'écrit ici ; la spécification vous est soumise d'abord.
- `kotlin-par-le-pilote` — le même moteur ; l'agent du pilote écrit l'adaptateur Kotlin, éprouvé ensuite ici.
- `un-adaptateur` — un adaptateur par projet ; l'adaptateur Kotlin s'écrit ici, et JustCook y ajoute Python.
- `refuser` — rien ne change ; l'agent revient avec d'autres pistes.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
