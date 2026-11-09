<!-- socle: couche=demandes zone=publique -->
# D-0088 — Valider une règle née des gênes du pilote : un correctif qui ne touche aucun fichier d'un adaptateur

> date : 2026-11-09

## Décision demandée

Valider qu'un correctif qui ne touche aucun fichier qu'un adaptateur juge
reste refusé, mais avec un message qui dit pourquoi et comment en sortir,
dont une issue nouvelle : une demande que vous validez, qui l'admet sans
test.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA : il tient la mémoire
du projet, et des contrôles automatiques vérifient ce que l'agent produit,
dans sa session, avant chaque commit, et dans la CI, les vérifications que
GitHub lance à chaque envoi. JustCook, votre application de cuisine, est le
projet pilote : l'agent qui y travaille vous rapporte ce qui le gêne dans
le socle, et vous me le transmettez.

**Le chantier.** Le 8 novembre, l'agent de JustCook vous a rapporté six
gênes. Ce 9 novembre, vous avez demandé qu'elles soient réglées avant la
prochaine mise à jour du socle installé dans JustCook. Trois sont réglées ;
les trois autres vous sont posées ce jour, chacune dans sa demande ;
celle-ci porte sur la deuxième.

**La question.** La règle ajoute une exception à celle qui veut qu'un
correctif livre un test : l'exception passe par votre validation, à chaque
fois, mais elle est vôtre à accorder.

### Ce qui gêne

Un adaptateur dit au socle, pour un langage, quels fichiers il juge (le
code, ses tests, et ses autres sources) et comment lancer les tests ; un
projet en a un par langage, le premier installé étant le principal. Un
commit de correctif, dont le titre commence par `fix:`, doit livrer un test
qui échoue sans lui : le socle le rejoue sur le commit d'avant. S'il ne
touche aucun fichier qu'un adaptateur juge, le socle le juge aujourd'hui
avec l'adaptateur principal, et exige un test de son langage.

Sur une branche d'essai de JustCook, un correctif en Dart, un langage
qu'aucun adaptateur ne couvrait, a ainsi fait échouer la CI : le socle
exigeait un test Python, le langage de l'adaptateur principal de JustCook,
sans rapport avec le code corrigé. Le correctif ne pouvait passer qu'en
retirant `fix:` de son titre, ou par un test Python fabriqué pour échouer.
JustCook écrit désormais son application en Kotlin, que le socle couvre ;
le cas reste pour tout fichier qu'aucun adaptateur ne juge : un autre
langage, mais aussi un fichier de construction comme `build.gradle.kts`,
que l'adaptateur Kotlin ne juge pas.

### La règle proposée

Un correctif qui ne touche aucun fichier qu'un adaptateur du projet juge
reste refusé, avec un message qui nomme ces fichiers et donne trois
issues :

- un adaptateur pour leur langage ;
- ces fichiers déclarés tiers : un fichier tiers, celui d'un outil copié
  dans le dépôt, échappe à tous les contrôles ; le déclarer assouplit un
  garde-fou (un réglage des contrôles du projet, que seule votre
  validation peut relâcher), et passe donc par une demande ;
- une demande que vous validez, qui nomme ce commit et l'admet sans test.
  Vous admettez déjà ainsi, depuis le 29 octobre, un correctif dont le test
  passe sur le commit d'avant parce que sa preuve dépend de
  l'environnement.

Un correctif qui touche un fichier qu'un adaptateur juge se juge comme
aujourd'hui.

## Éléments cités

Les numéros : B- un sujet du backlog, D- une demande, J- une entrée du
journal, datée et suivie de son rang dans la journée ; après @,
l'empreinte de la version que j'ai lue.

- B-0138@2592a463 — le sujet du correctif dans un langage qu'aucun
  adaptateur ne couvre, ouvert sur le retour de l'agent de JustCook.
- D-0047@b6b624e3 — votre réponse du 29 octobre : une demande validée qui
  nomme un correctif admet son test quand celui-ci passe déjà sur le commit
  d'avant.
- J-2026-11-08-S@b8e4e7e4 — le retour de l'agent de JustCook, le 8
  novembre, et ses six gênes.

## Où regarder

- [B-0138](https://github.com/theodubus/memory/blob/95a3f20d7268e6d860ad8ca14e2dabab425a6f34/memory/backlog/B-0138-tests-regression-exige-un-test-du-langage-de-l-ada.md) :
  la gêne telle que l'agent de JustCook l'a décrite.
- [La pull request en cours](https://github.com/theodubus/memory/pull/26),
  où la règle serait livrée.

## Options

- **Refusé, avec un message et une admission par demande** (recommandée) :
  ce qui est décrit plus haut. Effort : une heure, tests compris. Risque :
  une demande à valider par correctif admis, ce qui suppose ces correctifs
  rares. Aucun correctif ne passe sans preuve ni votre accord. Réversible.
- **Un simple avertissement** : le correctif passe, signalé. Plus léger,
  mais il passe sans preuve ni accord.
- **Rien** : le socle continue d'exiger un test du langage principal, sans
  issue claire.

## Conséquences

Si vous validez : j'écris la règle, ses tests et sa documentation, et je
la livre dans la pull request en cours. Si vous refusez, en disant quoi
changer (une autre option, ou rien), je fais ce que dit votre réponse. Sans
réponse, rien ne change ; selon votre consigne, la mise à jour de JustCook
attend vos réponses à ses gênes, mais vous pouvez la lancer sans elles.

## Recommandation

Valider. Vérifié : un correctif qui ne touche aucun fichier d'un
adaptateur se juge aujourd'hui par l'adaptateur principal, et l'adaptateur
Kotlin ne juge que les fichiers `.kt`. Supposé : que ces correctifs restent
rares ; aucune mesure ne le dit, JustCook n'ayant connu que le cas du Dart.

## Réponses possibles

- `valider` — la règle recommandée.
- `refuser` — l'agent fait ce que dit la réponse : une autre option, ou rien.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
