<!-- socle: couche=demandes zone=publique -->
# D-0083 — Valider la spécification des adaptateurs multiples : un projet en plusieurs langages, chaque fichier jugé par l'adaptateur de son langage (B-0095)

> date : 2026-11-08

## Décision demandée

Valider la spécification ci-dessous, écrite ici en entier : comment le
socle juge un projet écrit en plusieurs langages, chaque fichier par
l'adaptateur de son langage. Répondez dans la conversation par l'un des
mots de la fin ; une condition que vous y ajoutez sera recopiée mot pour
mot.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
sous forme de « demandes », des fichiers comme celui-ci, les décisions qui
vous reviennent. JustCook, votre application de cuisine, en est le
pilote : le premier projet réel équipé.

**Le chantier.** Le socle juge le code par un adaptateur : un fichier qui
dit, pour un langage, où sont les sources et les tests, comment
reconnaître un test, une assertion ou une fonction publique, comment
lancer les tests et mesurer la mutation (la part des défauts injectés que
les tests attrapent). Le socle en fournit dix, dits maintenus, chacun
éprouvé ici sur de vrais outils (Python, Java, Go…). Un projet n'en lit
qu'un. Cette nuit, vers minuit, vous avez validé qu'il en lise plusieurs,
pour JustCook, dont l'app sera en Kotlin et les outils sont en Python, et
que l'adaptateur Kotlin s'écrive ici, dans le dépôt du socle.

**La question.** Voici comment, avant que j'en écrive le code : le format,
la façon dont chaque règle choisit son adaptateur, et ce qui change pour
un projet à un seul langage, c'est-à-dire rien.

**Les mots.** Le moteur : le programme du socle. Un contrôle : une règle
qu'il vérifie à chaque fin de tour de l'agent, à chaque commit et dans la
CI, la vérification que GitHub lance à chaque envoi. `verify` : la
commande qui lance tout. L'état : le résumé que le socle calcule au début
de chaque session. Les garde-fous : le fichier des seuils du projet, dont
les plafonds de mutation, le nombre de défauts injectés que les tests
peuvent laisser passer dans un module. L'installeur : la commande qui
équipe un projet ou le met à jour. Un fichier protégé : il ne change
qu'avec votre accord, par une demande qui cite son empreinte. L'auto-test :
les défauts que le socle s'injecte pour prouver que ses contrôles les
attrapent, chacun avec un témoin sain qui doit passer. Le banc des
adaptateurs : le programme qui éprouve chaque adaptateur sur un petit
projet, avec ses vrais outils (mutmut et PIT sont les outils de mutation
de Python et de Kotlin).

**La spécification.**
1. *Le format.* `.socle/adapter.toml` reste où il est, pour qu'un projet
   à un seul langage ne change rien. Les autres adaptateurs vont dans
   `.socle/adapters/<nom>.toml`, au même format : une copie d'un adaptateur
   maintenu, ou un adaptateur propre au projet. Tous sont protégés, et tous
   jugent de la même façon : aucun ne passe avant un autre.
2. *Qui juge quel fichier.* Chaque adaptateur dit déjà quels fichiers il
   lit : ses sources (tout ce qu'il compile ou analyse), son code (ce qui
   doit être testé) et ses tests, par des motifs de chemins
   (`**/*.py` pour Python, `**/*.kt` pour Kotlin). Un fichier est jugé par
   l'adaptateur dont les motifs le désignent ; aucune clé nouvelle. Un
   contrôle nouveau refuse qu'un même fichier soit désigné par deux
   adaptateurs, en les nommant : l'ambiguïté se règle en resserrant les
   motifs d'une copie, par une demande. Un fichier qu'aucun ne désigne
   n'est pas jugé, comme aujourd'hui, et l'état le signale déjà quand son
   langage est présent. Écartée : une clé où chaque adaptateur déclarerait
   ses dossiers, inutile tant que les motifs suffisent ; elle reste la
   règle de repli s'ils ne suffisaient pas.
3. *Les règles des tests.* Le socle refuse un test qui ne vérifie rien,
   une valeur attendue changée sans votre accord, une fonction publique
   qu'aucun test ne nomme, et il signale un test désactivé : chaque fichier
   se juge avec les motifs de son adaptateur. Un correctif livre un test
   qui échoue sans lui dans le langage du code corrigé, rejoué par la
   commande de cet adaptateur ; s'il corrige du code des deux langages, un
   test dans chacun.
4. *La vérification.* `verify` lance la compilation, l'analyse du code et
   les tests de chaque adaptateur, l'un après l'autre, jusqu'au bout même
   après un échec, et nomme l'adaptateur de chaque étape qui échoue. La CI
   installe les outils de tous.
5. *La mutation.* Chaque adaptateur balaie ses modules avec son outil
   (mutmut pour Python, PIT pour Kotlin). Les plafonds restent tenus par
   module, dans les garde-fous : deux langages ne se mêlent pas. Le
   balayage planifié, chaque semaine, lance les outils de tous.
6. *L'installation et la mise à jour.* L'installeur accepte plusieurs
   adaptateurs (`--adapter python-pytest --adapter kotlin-gradle`), et, en
   automatique, en pose un par langage qu'il reconnaît ; le premier nommé
   prend `.socle/adapter.toml`, sans autre effet. La mise à jour rafraîchit chaque copie d'un
   adaptateur maintenu, que vous approuvez comme tout fichier protégé.
7. *Ce qui ne change pas.* Un projet à un seul langage ne change rien, et
   les dix adaptateurs maintenus restent tels quels. Le moteur ne connaît
   toujours aucun langage : tout ce qui en dépend reste dans les
   adaptateurs.
8. *Les preuves.* Des tests pour chaque règle à deux langages ; l'auto-test
   injecte un fichier désigné par deux adaptateurs, avec un témoin sain qui
   passe ; le banc éprouve un projet d'essai en Python et en Kotlin, avec
   les vrais outils.

**L'ordre.** D'abord l'adaptateur Kotlin pour Gradle, utile seul à un
projet tout en Kotlin, éprouvé par le banc, dès maintenant. Puis le moteur,
après votre réponse. Puis une version du socle, et la mise à jour de
JustCook, qu'une demande posée dans son dépôt vous fera approuver.
Quelques jours en tout.

**Ce qui reste supposé.** Que les motifs de chemins suffisent à départager
les adaptateurs d'un vrai projet : JustCook, ses langages séparés par
dossier et par extension, le dira. Sinon, je vous propose par une demande
une autre règle.

## Éléments cités

Les numéros : B- un sujet du backlog, D- une demande, J- une entrée du
journal, datée en temps universel et suivie de sa lettre dans la
journée ; après @, l'empreinte de la version que j'ai lue.

- D-0082@4e3bab7f — votre décision : plusieurs adaptateurs, l'adaptateur
  Kotlin écrit ici, la spécification soumise avant son code.
- J-2026-11-08-T@f0c8e1c3 — votre réponse à D-0082, mot pour mot.
- B-0095@65dbe4c6 — le sujet ouvert le 30 octobre : un projet à deux
  langages n'a qu'un adaptateur.

## Où regarder

- [D-0082](https://github.com/theodubus/memory/blob/14ce1c5ff5fb4cc0b7b20066d589f2496f213b89/memory/requests/D-0082-choisir-comment-le-socle-juge-un-projet-a-plusieur.md) :
  ce que vous avez choisi, pour vérifier que la spécification le suit.

## Options

- **Valider** (`valider`, recommandée) : effort, approuver ensuite la mise
  à jour de JustCook ; risque, une régression des contrôles, que les tests
  et l'auto-test attraperaient ; réversible, mais coûteux : le moteur
  change à une trentaine d'endroits, et JustCook s'y appuiera.
- **Refuser** (`refuser`) : effort nul ; JustCook attend une autre
  spécification ; réversible.

## Conséquences

Si vous validez, j'écris une décision de conception, au registre des
décisions du projet, qui recopie cette spécification, puis le moteur, ses tests et sa documentation, et je vous
dis quand JustCook peut se mettre à jour. Si vous refusez, en disant quoi
changer, je corrige et vous soumets le texte nouveau. Sans réponse, seul l'adaptateur Kotlin s'écrit,
et JustCook attend le reste.

## Recommandation

Valider. Vérifié : chaque adaptateur décrit déjà ses fichiers par des
motifs de chemins ; Python et Kotlin se séparent par leurs extensions ;
les plafonds de mutation sont déjà tenus par module. Supposé : que les
motifs suffisent sur un vrai projet ; JustCook le dira.

## Réponses possibles

- `valider` — la spécification est validée ; l'agent écrit la décision, puis le moteur.
- `refuser` — l'agent corrige ce que la réponse dit, et soumet une spécification nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
