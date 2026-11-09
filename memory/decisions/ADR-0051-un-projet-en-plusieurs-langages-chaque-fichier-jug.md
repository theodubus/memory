<!-- socle: couche=decisions zone=publique -->
# ADR-0051 — Un projet en plusieurs langages : chaque fichier jugé par l'adaptateur dont les motifs le désignent

> statut : acceptée · date : 2026-11-09 · validation : D-0083@054ce997 · source : B-0095@65dbe4c6, J-2026-11-08-S@b8e4e7e4, D-0082@4e3bab7f · lu : decisions@43d3f4e0

## Contexte

Le socle juge le code d'un projet par un adaptateur, et n'en lisait
qu'un : un langage qu'il ne lit pas échappe à toutes les règles sur les
tests. JustCook, le pilote, écrit son app en Kotlin sous Gradle, à côté
d'outils Python (J-2026-11-08-S@b8e4e7e4). Théo a choisi que le socle gère
plusieurs adaptateurs par projet, et que l'adaptateur Kotlin s'écrive ici
(D-0082@4e3bab7f) ; puis il a validé la spécification, soumise en entier
dans D-0083. Elle est recopiée ici mot pour mot.

## Décision

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
   adaptateurs (`--adapter python-pytest --adapter kotlin`), et, en
   automatique, en pose un par langage qu'il reconnaît ; le premier nommé
   prend `.socle/adapter.toml`, sans autre effet. La mise à jour rafraîchit chaque copie d'un
   adaptateur maintenu, que vous approuvez comme tout fichier protégé.
7. *Ce qui ne change pas.* Un projet à un seul langage ne change rien, et
   les neuf adaptateurs maintenus restent tels quels. Le moteur ne connaît
   toujours aucun langage : tout ce qui en dépend reste dans les
   adaptateurs.
8. *Les preuves.* Des tests pour chaque règle à deux langages ; l'auto-test
   injecte un fichier désigné par deux adaptateurs, avec un témoin sain qui
   passe ; le banc éprouve un projet d'essai en Python et en Kotlin, avec
   les vrais outils.

« Les neuf adaptateurs maintenus » : neuf avant `kotlin`, qui fait le
dixième. Le « vous » de la spécification est Théo.

## Conséquences

L'adaptateur `kotlin` s'est écrit d'abord, utile seul à un projet tout en
Kotlin. D-0083 décrivait deux changements du moteur qu'il demandait ; la
revue adversariale en a remplacé un (J-2026-11-09-B@547d0508) : le verdict
de mutation ne cherche plus un module par son plus long suffixe, qui
pouvait lui prêter les résultats d'un homonyme ; le lecteur de PIT
retrouve le vrai fichier de chaque mutation, par son paquet.

Ce qui reste supposé, tel que D-0083 le dit : que les motifs de chemins
suffisent à départager les adaptateurs d'un vrai projet ; JustCook, ses
langages séparés par dossier et par extension, le dira. Sinon, une
demande propose une autre règle, la clé de dossiers écartée au point 2
d'abord. La défaire : une demande ; un projet à plusieurs adaptateurs
revient à un seul, et le reste de son code cesse d'être jugé.
