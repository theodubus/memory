<!-- socle: couche=demandes zone=publique -->
# D-0085 — Choisir ce que la mise à jour du socle rafraîchit dans les adaptateurs d'un projet

> date : 2026-11-09

## Décision demandée

Choisir ce qu'une mise à jour du socle fait des copies d'adaptateurs qu'un
projet possède déjà. Attention : la réponse recommandée, `valider`, n'est
pas ce que fait le code fusionné ; elle le change.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA, et qui vérifie ce que
l'agent produit. JustCook, votre application de cuisine, en est le pilote,
et pour l'instant le seul projet équipé.

**Le chantier.** Le 8 novembre, vous avez validé qu'un projet écrit en
plusieurs langages ait un adaptateur par langage ; c'est livré et fusionné
ce 9 novembre. Un adaptateur est un fichier de réglages qui dit au socle,
pour un langage, comment lancer les tests, reconnaître un test qui ne
vérifie rien, et quels fichiers il juge : ceux que ses motifs de chemins
désignent, comme `**/*.py`. Le socle en maintient dix ; un projet en reçoit
une copie, protégée. La copie principale, `.socle/adapter.toml`, est celle
du premier langage installé : pour JustCook, Python, ses outils existant
avant l'app ; les autres vont dans un dossier à part, .socle/adapters.
Reste à publier une version nouvelle du socle, dont JustCook se met à
jour : il recevra une copie de l'adaptateur Kotlin.

**La question.** La spécification que vous avez validée dit deux choses
qui ne s'accordent pas, et j'ai tranché seul ; la revue de mon travail,
faite par un second agent qui cherche mes défauts, l'a relevé.

Le point 6 de la spécification dit : « La mise à jour rafraîchit chaque
copie d'un adaptateur maintenu, que vous approuvez comme tout fichier
protégé. » Le point 7 dit : « Un projet à un seul langage ne change rien. »
Aujourd'hui, une mise à jour garde toujours la copie principale telle
quelle. J'ai donc choisi de ne rafraîchir que les copies des autres
langages : c'est ce que fait le code fusionné (`autres-langages`
ci-dessous).

Rafraîchir apporte au projet les corrections d'un adaptateur maintenu sans
autre démarche : ce matin, une revue a trouvé dix défauts dans
l'adaptateur Kotlin, corrigés depuis. Mais deux faits pèsent contre :

- **Une copie s'adapte au projet.** Un projet y ajoute des commandes que
  la vérification lance en plus (un banc de performance), y nomme les
  fichiers que la mutation doit couvrir quand son code n'est pas sous
  `src/`, et un projet Android comme JustCook y change les commandes de
  Gradle, l'outil qui construit et teste une app Kotlin. Rafraîchie, la
  copie redevient identique à l'adaptateur maintenu : l'adaptation est
  perdue, et se refait par une demande.
- **Une copie se resserre.** Le point 2 dit qu'un fichier que deux
  adaptateurs désignent se règle en resserrant les motifs d'une copie, par
  une demande. Rafraîchie, la copie perd ce resserrement, et le contrôle
  qui refuse un fichier désigné deux fois échoue : il bloque le commit et
  la CI du projet jusqu'à une demande nouvelle.

Votre approbation ne les protège pas. En session cloud, l'agent du projet
(celui de JustCook) vous pose, après une mise à jour, une demande qui cite
chaque fichier protégé changé ; vous l'acceptez ou la refusez en entier.
Refuser bloque toute la mise à jour, pas une seule copie.

Une voie intermédiaire existe, que je vous recommande. Le socle installé
dans le projet garde ses adaptateurs maintenus : à la mise à jour,
l'installeur sait donc si une copie est restée identique à la version
qu'il avait posée. Restée identique, elle n'est pas adaptée, et se
rafraîchit sans rien perdre. Adaptée, elle se garde, et l'installeur dit
seulement quand l'adaptateur maintenu a changé depuis : l'agent du projet
vous propose alors, par une demande, d'y reporter les corrections.

## Éléments cités

Les numéros : D- une demande, ADR- une décision du projet, J- une entrée du
journal, B- un sujet du backlog ; après @, l'empreinte de la version que
j'ai lue.

- D-0083@054ce997 — votre validation de la spécification, dont les points
  2, 6 et 7 sont cités plus haut.
- ADR-0051@96428594 — la décision qui recopie cette spécification, mêmes
  numéros, dans le registre des décisions du projet ; votre réponse ici
  remplacera son point 6 par une décision nouvelle.
- J-2026-11-09-H@94a255f0 — le compte rendu de la revue de mon travail, dont
  le constat 10 relève que j'avais tranché seul.
- B-0095@65dbe4c6 — le sujet ouvert le 30 octobre : un projet à deux
  langages n'avait qu'un adaptateur.

## Où regarder

- [D-0083](https://github.com/theodubus/memory/blob/88596a8253fe73a6676f0cc3fbcff4325c0bd679/memory/requests/D-0083-valider-la-specification-des-adaptateurs-multiples.md) :
  les points 2, 6 et 7, pour vérifier qu'ils sont cités fidèlement.
- [La documentation des adaptateurs](https://github.com/theodubus/memory/blob/88596a8253fe73a6676f0cc3fbcff4325c0bd679/engine/socle/adapters/README.md) :
  la section « Un projet en plusieurs langages », ce que la mise à jour
  fait aujourd'hui ; la section « Kotlin », sa dernière phrase, qui dit
  qu'un projet Android adapte les commandes dans sa copie.

## Options

Toutes posent la copie Kotlin de JustCook, qu'il n'a pas encore, et toutes
se défont par une demande ; une adaptation déjà perdue se refait par une
demande.

- **Rafraîchir les seules copies que le projet n'a pas adaptées**
  (`valider`, recommandée), principale comprise : une copie adaptée se
  garde, et la mise à jour dit quand son adaptateur maintenu a changé.
  Effort : une demi-journée, et ses tests. Risque : une copie adaptée qui
  vieillit si personne ne donne suite. Le point 7 change, mais un projet à
  un seul langage n'y perd rien : seule une copie non adaptée change.
  Réversible.
- **N'en rafraîchir aucune** (`aucune`) : la mise à jour pose les copies
  qui manquent et dit, à chaque fois, celles qui diffèrent de l'adaptateur
  maintenu, adaptées ou non. Effort : quelques lignes. Risque : le même
  constat répété pour une copie adaptée, qui devient du bruit. Réversible.
- **Ne rafraîchir que les copies des autres langages** (`autres-langages`) :
  le code fusionné. Effort nul. Risque : la copie Kotlin de JustCook,
  adaptée à Android, est remise à l'identique à chaque mise à jour.
  Réversible.
- **Tout rafraîchir, principale comprise** (`tout-rafraichir`) : le point
  6 au pied de la lettre. Effort : quelques lignes. Risque : toute copie
  adaptée, même d'un projet à un seul langage, perd son adaptation à
  chaque mise à jour. Réversible.

## Conséquences

Si vous validez, le point 6 devient : « La mise à jour rafraîchit chaque
copie d'un adaptateur maintenu que le projet n'a pas adaptée ; une copie
adaptée se garde, et la mise à jour dit quand son adaptateur maintenu a
changé. » J'écris la décision, puis le code et ses tests, avant la version
du socle. Une autre option se traite de même, avec son texte. Si vous
refusez, en disant quoi changer, je corrige et vous soumets le texte
nouveau. Sans réponse, le code fusionné reste tel quel, et je ne publie
pas la version qui mettrait JustCook à jour.

## Recommandation

Rafraîchir les seules copies non adaptées. Vérifié : le socle installé
dans un projet garde ses adaptateurs maintenus, que l'installeur lit avant
de le remplacer ; la documentation prévoit qu'un projet adapte sa copie ;
votre approbation porte sur la mise à jour entière. Supposé : que l'agent
d'un projet donne suite au constat d'un adaptateur maintenu qui a changé.
Je ne sais pas si la copie Python de JustCook est adaptée aujourd'hui : je
ne lis pas son dépôt ; aucune option sauf `tout-rafraichir` ne la touche
si elle l'est.

## Réponses possibles

- `valider` — seules les copies non adaptées se rafraîchissent, principale comprise ; ce n'est pas le code fusionné.
- `aucune` — aucune copie ne se rafraîchit ; la mise à jour dit celles qui diffèrent.
- `autres-langages` — seules les copies des autres langages se rafraîchissent, comme le code fusionné.
- `tout-rafraichir` — toutes les copies se rafraîchissent, la principale comprise.
- `refuser` — l'agent corrige ce que la réponse dit, et soumet une demande nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
