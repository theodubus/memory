<!-- socle: couche=demandes zone=publique -->
# D-0191 — Choisir ce que le socle fait d'un projet Kotlin multiplateforme ou Android, que la copie kotlin des adaptateurs ne sert pas : l'installeur et la spécification le disent, une variante maintenue, ou des commandes qui échouent en le disant

> date : 2026-11-25

## Décision demandée

Choisir ce que fait le socle d'un projet Kotlin multiplateforme ou Android, où les commandes de l'adaptateur `kotlin` peuvent sauter des tests sans erreur : l'installeur et la spécification signalent que des tests seraient sautés, avec les commandes à mettre (recommandé) ; la spécification seule ; une variante maintenue de l'adaptateur ; ou des commandes qui échouent en le disant.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Pour vérifier, il lance les commandes d'un adaptateur, un fichier par langage, rangé dans le moteur, qui dit comment compiler, lancer les tests et mesurer la mutation (la part des défauts introduits exprès que les tests attrapent). Chaque projet en reçoit une copie, `.socle/adapter.toml`, qu'il peut modifier, et qu'une mise à jour garde.

**Le chantier.** Le jalon en cours corrige et stabilise le produit avant que chess, votre jeu d'échecs, reçoive la nouvelle version du socle. Le 21 novembre, vous avez fait découper en lots les besoins restants du jalon ; celui-ci vient du retour du pilote, le 10 novembre : JustCook, le projet où le socle est essayé en usage réel. C'est le dernier lot du jalon qui ne vous a encore rien soumis ; les deux autres passent avant lui.

**La question.** L'adaptateur `kotlin` suppose des modules JVM : du Kotlin compilé pour la machine virtuelle Java, le cas ordinaire d'un serveur ou d'une bibliothèque, sous Gradle, l'outil de construction de Kotlin. JustCook, une application Compose Multiplatform (du code Kotlin partagé entre Android, iOS et le bureau), n'y entre pas : il a dû adapter sa copie, par une demande. Que doit faire le socle pour le prochain projet de ce genre ?

**Ce que font les trois commandes.** Mesuré ce 25 novembre sur des projets d'essai (Kotlin 2.0.21, Gradle 8.14.3), sauf Android, que rapporte JustCook :

- un module multiplateforme n'a pas de tâche `test` : ses tests se lancent par `allTests`, qui les lance et échoue bien sur un test faux ;
- **un projet mixte**, un module JVM et un module multiplateforme dont le test échoue exprès : la compilation (`./gradlew -q testClasses`) et les tests (`./gradlew -q test`) réussissent, sans lancer ce test ; le socle dirait les tests verts ;
- un projet multiplateforme seul : les deux commandes échouent, en disant que la tâche manque ;
- un module Android, le cas de JustCook : la compilation échoue (`testClasses` n'y existe pas) ; `test` y lance les tests unitaires ;
- la mutation (`./gradlew -q pitest`) : son greffon ne gère que les modules JVM.

JustCook a donc vu un échec bruyant ; le cas silencieux, le plus grave, n'a été vu que sur le projet d'essai. La spécification des adaptateurs dit déjà qu'un tel projet « adapte les commandes dans sa copie », sans dire lesquelles ni que des tests peuvent être sautés ; rien ne le dit à l'installation. Des projets que ce dépôt connaît, chess et JustCook, seul JustCook emploie Kotlin, et sa copie est déjà adaptée. Au regard de votre décision du 24 novembre, des tests sautés en silence sont un bug important, car ils faussent la vérification ; mais rare, car il faut un projet mixte : d'où une option qui coûte peu.

## Éléments cités

- B-0147@ad3ae83e — le besoin, satisfait aujourd'hui quand « un projet Compose Multiplatform ou Android a des commandes de compilation et de tests qui lancent ses tests, ou échouent en le disant, et la spécification des adaptateurs dit ce que la copie `kotlin` suppose ».
- T-0151@91ac86dc — la tâche qui vous soumet cette demande ; votre réponse la clôt.
- T-0152@6359a441 — la tâche qui appliquera l'option retenue.
- L-0032@af5a7cbc — le lot de ces deux tâches, au jalon en cours.
- J-2026-11-10-H@a5473f3b — le retour du pilote du 10 novembre, qui relève le problème.
- D-0165@d8aaca8b — votre décision du 24 novembre : du temps pour un bug important, aucun pour un cas limite rare que l'agent gère lui-même.

## Où regarder

- [La spécification des adaptateurs](https://github.com/theodubus/memory/blob/9442e1c06b0c7dd74ff136d64a6b89e8a46719e9/engine/socle/adapters/README.md), section « Kotlin », son dernier paragraphe : ce qu'elle dit aujourd'hui d'un projet multiplateforme ou Android.
- [L'adaptateur `kotlin` du moteur](https://github.com/theodubus/memory/blob/9442e1c06b0c7dd74ff136d64a6b89e8a46719e9/engine/socle/adapters/kotlin.toml), dont chaque projet reçoit la copie : ses commandes `build`, `tests` et `mutation`, et le commentaire de tête, qui le dit aussi.

## Options

- **Le signaler à l'installation et dans la spécification** (recommandée). L'installeur, à l'installation comme à la mise à jour, reconnaît dans les fichiers de Gradle un module multiplateforme ou Android (ses greffons, écrits en clair ou dans le catalogue des versions, le fichier où Gradle range les versions) ; tant que la copie garde les commandes JVM, il avertit, sans bloquer, dans ce qu'il imprime à l'agent du projet, que des tests seraient sautés, et nomme les commandes à mettre : `allTests` pour les tests d'un module multiplateforme, sa compilation par cible (une plateforme visée : Android, iOS, le bureau), la mutation déclarée absente hors JVM (son contrôle ne tourne pas, et l'état le dit). La spécification les donne. Effort : une tâche, de 2 à 4 points de la semaine (un point : 1 % de la limite d'usage hebdomadaire de votre compte), avec sa note de version. Risque : l'agent du projet doit encore adapter sa copie, et s'il passe outre, les tests restent sautés ; un module ajouté après l'installation n'est signalé qu'à la mise à jour suivante. Réversible.
- **La spécification seule** : elle dit ce que suppose l'adaptateur et donne les mêmes commandes, sans rien dans l'installeur. Effort : un point. Risque : rien ne le dit au projet qui s'installe. Réversible.
- **Une variante maintenue `kotlin-multiplatform`** : un second adaptateur, que l'installeur choisit sur un tel build ; tests par `allTests`, compilation par cible, mutation absente ou bornée aux modules JVM ; éprouvé par le banc des adaptateurs (un projet jetable par langage, où chaque contrôle est essayé) et par la CI de GitHub. Effort : deux tâches, de 6 à 8 points, puis son entretien à chaque changement des adaptateurs. Risque moyen : iOS ne se compile que sur macOS, Android exige son kit de développement, absent du conteneur où l'agent travaille, et la variante n'en éprouverait qu'une part. Réversible.
- **Des commandes qui échouent en le disant** : les commandes de l'adaptateur passent par un script d'initialisation de Gradle, posé par le socle, qui échoue avec un message quand un module porte du Kotlin sans la tâche visée ; la spécification donne les commandes, la mutation reste déclarée absente hors JVM. Effort : une tâche, de 3 à 4 points, éprouvée sur des projets d'essai. Risque : un script à tenir à jour avec Gradle et le greffon Android ; le projet doit encore adapter sa copie, mais aucun test n'est plus sauté en silence, même dans un module ajouté plus tard. Réversible.

## Conséquences

Si vous validez : T-0151 se ferme ; T-0152 applique la première option dans ce lot, dans une prochaine session : l'installeur et ses tests, sur des fichiers de Gradle d'essai, sans lancer Gradle ; la spécification ; la note de version. Le critère du besoin passe de commandes qui lancent les tests ou échouent à un avertissement de l'installeur et des commandes données par la spécification. Ni JustCook, à la copie adaptée, ni chess n'ont rien à faire, et la mise à jour de chess n'attend qu'un lot de quelques points. Avec une autre option : T-0152 se récrit sur elle ; la variante retarde d'autant cette mise à jour. Si vous refusez : dites ce qui change, une combinaison comprise ; la demande se réécrit et revient. Sans réponse : rien ne change, ce lot attend, et l'agent passe au suivant.

## Recommandation

Le signaler à l'installation et dans la spécification : le seul projet Kotlin connu a déjà sa copie adaptée, et c'est à l'installation qu'un projet nouveau prend des commandes qui sauteraient ses tests ; l'option coûte peu et se teste sans Gradle. Si vous tenez à ce qu'aucun test ne soit jamais sauté en silence, les commandes qui échouent en le disant. Vérifié : les comportements du module multiplateforme, du projet mixte et du projet multiplateforme seul, sur les projets d'essai. Supposé : le comportement d'un module Android, que rapporte JustCook, sans changer le choix ; les commandes de sa copie, que ce dépôt ne lit pas ; que la reconnaissance des greffons couvre les builds réels, ce que les tests de T-0152 vérifieront sur un build de Compose Multiplatform.

## Réponses possibles

- `valider` — l'installeur et la spécification le signalent, avec les commandes à mettre.
- `specification-seule` — la spécification seule le dit.
- `variante` — une variante maintenue `kotlin-multiplatform`.
- `commandes-qui-echouent` — des commandes qui passent par un script qui échoue en le disant.
- `refuser` — aucune de ces options : dites ce qui change ; la demande se réécrit et revient.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
