<!-- socle: couche=demandes zone=publique -->
# D-0076 — Corriger le skill socle-review sur deux constats de sa première revue : ce que le relecteur voit, et sa description

> date : 2026-11-05

## Décision demandée

Valider deux corrections du skill `socle-review`, relevées par sa première
revue : sa description, qui le réservait encore « à un projet qui
l'applique », et la phrase qui disait faussement ce que le relecteur ne
voit pas.

## Contexte

Vous avez validé le skill de la revue adversariale (D-0074), puis fait de
la revue la règle de tout projet (D-0075). Le premier lot que ce dépôt a
fait relire, celui de ces deux décisions, a reçu six constats. Quatre sont
traités. Deux touchent le texte du skill, que vous avez validé tel quel :
il ne change pas sans vous.

Le premier constat : la description du skill, ce que l'agent lit pour
décider de le charger, dit « dans un projet qui l'applique ». C'était vrai
quand la revue était une option. Depuis D-0075, tout projet l'applique, et
ces mots invitent l'agent à se demander si la sienne s'en dispense.

Le second constat : le skill dit que le relecteur n'a « ni la conversation,
ni la mémoire, ni l'état ». Sous Claude Code, c'est faux : un sous-agent
lancé dans le dépôt reçoit les instructions du projet et peut le lire. Ce
qu'il n'a pas, c'est la conversation et le raisonnement de l'agent qui a
écrit le lot ; c'est cela qui lui fait voir ce que l'agent ne voit plus.

Les corrections :
- la description finit à « …une spécification ou un test. » ;
- le troisième pas du skill devient : « Le confier à un relecteur qui n'a
  pas la conversation. Sous Claude Code : un sous-agent (outil `Agent`), du
  modèle de la session, dont le seul message est ce dossier, tel quel :
  rien ne s'y ajoute, rien ne s'en retire. Il reçoit aussi les
  instructions du projet et peut lire le dépôt, mais ni la conversation ni
  le raisonnement de l'agent, et le dossier lui dit de ne rien modifier.
  Un agent sans sous-agents saute la revue, et son récap le dit. »

« Rien ne s'en retire » est ajouté parce que, pour cette première revue,
j'ai abrégé quatre des demandes citées dans le dossier : l'écart vous a été
dit, et la règle l'écrit. Le gabarit anglais change de même. Le fichier
protégé de ce dépôt, `.claude/skills/socle-review/SKILL.md`, aurait alors
l'empreinte `sha256:e2da29beea4e79c5`.

## Éléments cités

- D-0074@a5cc393b — la demande par laquelle vous avez validé le skill tel
  qu'il est aujourd'hui.
- D-0075@d38d362d — la demande par laquelle vous avez fait de la revue la règle
  de tout projet.
- ADR-0043@9be187f0 — la décision qui l'écrit au registre des décisions.
- J-2026-11-05-D@e9024022 — l'entrée du journal qui donne les six constats
  de la première revue, et ce que chacun est devenu.
- `.claude/skills/socle-review/SKILL.md` et `sha256:e2da29beea4e79c5` — le
  fichier protégé de ce dépôt, et son empreinte une fois corrigé.

## Où regarder

- [le skill aujourd'hui](https://github.com/theodubus/memory/blob/6e80c8ce6a7e4c30c05864925e0ee1a8bd97ff8c/.claude/skills/socle-review/SKILL.md) : la description, à la ligne 3, et le
  troisième pas, lignes 31 à 35, que les corrections remplacent.

## Options

- **Valider** : l'agent applique les deux corrections au skill, en deux
  langues, et à sa copie dans ce dépôt ; effort nul pour vous ; risque
  faible, deux phrases plus justes ; réversible.
- **Refuser** : le skill reste tel quel ; effort nul ; risque, l'agent
  d'un projet lit une description qui contredit ses instructions, et un
  relecteur décrit autrement qu'il n'est ; réversible.

## Conséquences

Si vous validez, les corrections se commitent dans la pull request en
cours, et tout projet les reçoit à sa prochaine mise à jour. Si vous
refusez, le skill reste tel que D-0074 l'a validé. Sans réponse, rien ne
change, et l'agent travaille sur autre chose.

## Recommandation

Valider. Vérifié : la description contredit la règle de D-0075, et la revue
de ce lot a reçu les instructions du projet, ce que la phrase actuelle
nie. Supposé : rien d'autre ; les deux corrections ne changent pas ce que
fait la revue, seulement ce qu'en dit le skill.

## Réponses possibles

- `valider` — les deux corrections s'appliquent au skill, en deux langues, et à sa copie dans ce dépôt.
- `refuser` — le skill reste tel quel.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
