<!-- socle: couche=demandes zone=publique -->
# D-0079 — Valider la nouvelle version du skill socle-request de ce dépôt, qui fait relire chaque demande à froid avant de vous la poser (B-0130)

> date : 2026-11-08

## Décision demandée

Valider le texte nouveau du skill `socle-request` dans ce dépôt : sa copie
protégée, `.claude/skills/socle-request/SKILL.md`, dont l'empreinte devient
`sha256:39d97f7bcbef768a`.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
sous forme de « demandes », des fichiers comme celui-ci, les décisions qui
vous reviennent. Ce dépôt utilise lui-même le socle qu'il fabrique.

**Le chantier.** Le 8 novembre, vous avez signalé qu'une demande de
JustCook, le projet pilote sur lequel vous essayez le socle, ne vous
remettait pas en contexte, et vous avez validé ma proposition le
jour même : le contexte de chaque demande commence par trois paragraphes,
le projet, le chantier et la question, et chaque demande est relue à froid
avant de vous être posée. Le code est écrit : les modèles de demande, le
contrôle qui refuse une demande sans ces paragraphes, et la commande qui
prépare la relecture. Il est dans [la pull request #24](https://github.com/theodubus/memory/pull/24), qui reste
rouge tant que cette demande attend : le socle refuse un fichier protégé
changé sans votre accord.

**La question.** Reste le skill `socle-request` : la procédure écrite que
l'agent suit pour vous poser une demande. Le socle le pose dans chaque
projet qu'il équipe, depuis un modèle de son code, en français ou en
anglais selon le projet ; ce dépôt, équipé comme les autres, en a une
copie. Le modèle a changé avec le code, dans les deux langues. La copie de
ce dépôt est protégée : elle ne change qu'avec votre accord, et c'est elle
seule que porte votre réponse, comme le 5 novembre pour le skill de la
revue du code. Le texte change à deux endroits, recopiés ci-dessous mot
pour mot ; le reste est inchangé, sinon que l'ancienne étape 4,
« Commiter et pousser la demande », devient l'étape 5.

**Premier changement, au champ « Contexte » de l'étape 2.** L'ancien texte
disait : « le problème lui-même, résumé sur place en au moins soixante
mots, pas un renvoi ». Le nouveau :

> **Contexte** : pour l'humain qui revient sur le projet après des
> semaines, trois paragraphes d'abord, chacun ouvert par son nom en gras :
> **Le projet.** (ce qu'il fait, et pour qui, même si l'humain le sait),
> **Le chantier.** (le but du travail en cours, ce qui est fait et ce qui
> reste ; ses décisions passées dites par leur contenu et leur date, pas
> par leur numéro) et **La question.** (ce qui la pose maintenant). Puis
> le détail, sur place, pas un renvoi : soixante mots au moins en tout, et
> chaque terme propre au projet expliqué à sa première apparition.

Le seuil de soixante mots ne bouge pas : le contrôle l'a toujours compté
sur toute la section.

**Second changement, une étape 4 ajoutée, avant l'étape qui commite et
pousse la demande :**

> La faire relire à froid avant de la pousser : un sous-agent (outil
> `Agent`), du modèle de la session, dont le seul message est le dossier
> de `python3 .socle/socle review --request D-NNNN`, tel quel. Il lit la
> demande dans le rôle de l'humain qui n'a pas ouvert le projet depuis
> trois semaines, sans lien ni fichier, et rend ce qu'il en a compris et
> ce qui lui manque pour décider. Réécrire ce que l'humain ne
> comprendrait pas davantage ; écarter, d'une raison, ce qui n'aide pas à
> décider ou qu'un document lié donne déjà. Le récap le dit : `Relecture
> à froid : <n> points, <k> corrigés ; écartés : …`. Un agent sans
> sous-agents saute cette étape, et son récap le dit.

Le sous-agent est un second agent que je lance avec ce seul texte ; le
récap, le résumé qui clôt chacune de mes interventions. Ces détails, le
modèle de la session et le cas d'un agent sans sous-agents, viennent de la
décision que D-0078 vous soumettait.

**La consigne exacte que reçoit le relecteur**, imprimée par cette
commande avant le texte de la demande :

> Tu es l'humain à qui cette demande s'adresse. Tu n'as pas ouvert ce
> projet depuis trois semaines : tu ne te souviens ni de ce qu'il fait en
> détail, ni du travail en cours, ni de ce que tu as décidé avant. Tu n'as
> que le texte ci-dessous : n'ouvre aucun lien, ne lis aucun fichier, ne
> cherche rien. Lis la demande, puis rends, sans rien modifier nulle
> part : 1. le projet et le but du travail en cours, en tes mots, tels que
> la demande te les apprend ; « je ne sais pas » pour ce qu'elle ne dit
> pas ; 2. la décision qu'on te demande, et ce que change chacune des
> réponses possibles ; 3. chaque mot, nom, sigle ou renvoi que le texte
> emploie sans te l'expliquer, avec la phrase où il apparaît ; 4. ce qu'il
> te manquerait pour décider sans aller chercher ailleurs. Ne juge pas si
> la décision est bonne : seulement si le texte seul te permet de la
> prendre.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision de conception, D-
une demande ; après @, l'empreinte de la version que j'ai lue, une somme de
contrôle de son texte.

- D-0078@c7bdf1a6 — votre validation du 8 novembre : trois paragraphes en
  tête du contexte, et une relecture à froid de chaque demande.
- ADR-0046@75188a70 — la décision qui l'écrit, acceptée sur votre réponse.
- B-0130@ac56745f — le sujet ouvert sur votre retour ; il se ferme avec
  cette validation.
- D-0074@a5cc393b — le précédent du 5 novembre : la copie protégée du
  skill de la revue du code, validée de la même façon.
- #24 — la pull request qui porte le code de cette règle et la copie
  nouvelle du skill, rouge tant que cette demande attend.
- `.claude/skills/socle-request/SKILL.md` et `sha256:39d97f7bcbef768a` — le
  fichier protégé de ce dépôt qui change, et l'empreinte de son texte
  nouveau.

## Où regarder

- [La version actuelle du skill](https://github.com/theodubus/memory/blob/dc40afbd6445352f554e34ff1a25eec1ea5a0b7e/.claude/skills/socle-request/SKILL.md) :
  le champ « Contexte » de l'étape 2, que remplace le premier passage, et
  l'étape 4, « Commiter et pousser », avant laquelle s'insère le second.
- [La pull request #24](https://github.com/theodubus/memory/pull/24) : le
  code, et la copie nouvelle du skill dans son diff.
- [D-0078](https://github.com/theodubus/memory/blob/dc40afbd6445352f554e34ff1a25eec1ea5a0b7e/memory/requests/D-0078-valider-la-specification-qui-fait-remettre-en-cont.md) :
  ce que vous avez validé, pour vérifier que le skill le dit.

## Options

- **Valider** (`valider`, recommandée) : effort nul ; le skill de ce dépôt
  suit la règle que vous avez validée ; risque faible, le texte ne fait que
  l'écrire ; réversible, comme tout fichier protégé, par une autre demande.
- **Refuser** (`refuser`) : effort nul ; la copie de ce dépôt reste
  l'ancienne ; risque, l'agent de ce dépôt n'y trouve ni les trois
  paragraphes, que le contrôle exige pourtant, ni la relecture ;
  réversible.

## Conséquences

Si vous validez, je consigne votre réponse : la vérification de la pull
request #24 passe au vert, et B-0130 se ferme. Les projets équipés le
reçoivent à leur mise à jour, que leur humain approuve comme les autres
fichiers protégés qu'elle change. Si vous refusez, le code reste
dans la pull request, qui reste rouge, et je reviens vers vous avec le
texte à changer. Sans réponse, la pull request reste rouge, et je
travaille sur autre chose.

## Recommandation

Valider. Vérifié : les deux passages disent ce que D-0078 a validé, le
skill passe ses contrôles en deux langues, et l'auto-test du socle, qui
injecte des défauts pour vérifier que ses contrôles les attrapent, attrape
une demande sans les trois paragraphes. Supposé : que la consigne du
relecteur, la même qu'aux relectures que j'ai faites le 8 novembre, de la
demande du pilote puis de D-0078, convient à toute demande.

## Réponses possibles

- `valider` — la copie nouvelle du skill est validée ; la pull request passe au vert, et B-0130 se ferme.
- `refuser` — la copie reste l'ancienne ; l'agent revient avec le texte à changer.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
