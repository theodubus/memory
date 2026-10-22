<!-- socle: couche=demandes zone=publique -->
# D-0040 — Choisir comment éviter qu'une demande à plusieurs réponses positives ne valide rien (B-0081)

> date : 2026-10-22 · lu : decisions@2a93e7ab

## Décision demandée

Choisir la règle qui empêche qu'une demande dont la réponse devait
autoriser un geste réservé à l'humain (supprimer un test, changer une
valeur attendue, relâcher un seuil) soit répondue sans rien autoriser.

## Contexte

Le moteur ne tient une demande pour validée que si la réponse est
`valider` (ou `approve` en anglais). Les deux contrôles qui acceptent une
validation la cherchent ainsi : celui des tests protégés lit, dans le
texte d'une demande validée, le nom de chaque test supprimé ou changé ;
le cliquet des seuils y lit la clé du seuil relâché.

Le 20 octobre, la demande sur le retrait du code de compatibilité offrait
trois réponses : `tout`, `compatibilite-seule` et `refuser`. Théo a
répondu `tout`. Cette réponse ne s'appelait pas `valider` : elle n'a donc
débloqué aucun des tests que la demande nommait, et il a fallu reposer la
même question sous la forme `valider` / `refuser`, test par test. Rien ne
signalait la faute à la rédaction : la demande passait le lint.

Le défaut est dans l'outil : il laisse écrire une demande qui ne peut rien
autoriser alors qu'elle en a l'air. Le corriger touche à ce qui autorise
l'agent ; la règle se choisit donc avec Théo.

## Éléments cités

- B-0081@4cf3bf01 — le sujet du backlog qui décrit ce défaut et ses deux
  voies de correction.
- D-0033@43487fd4 — la demande sur le retrait du code de compatibilité,
  aux réponses `tout`, `compatibilite-seule` et `refuser`.
- D-0035@984515f3 — la demande reposée sous la forme `valider` /
  `refuser`, test par test, que Théo a validée.
- ADR-0004@24c869b4 — la décision qui fait d'une validation une réponse
  `valider` ajoutée, qui cite ce qu'elle valide.

## Où regarder

- [la demande sur le code de compatibilité](https://github.com/theodubus/memory/blob/13223681bf85ce7b842ee5deb2621736a66f5f1b/memory/requests/D-0033-retirer-le-code-de-compatibilite-avec-les-versions.md),
  section « Réponses possibles » : vérifier qu'aucune réponse ne
  s'appelait `valider`.
- [le modèle des demandes](https://github.com/theodubus/memory/blob/13223681bf85ce7b842ee5deb2621736a66f5f1b/engine/socle/requests.py),
  propriété `validee` : une demande est validée si sa réponse est
  `valider`, et rien d'autre.
- [le guide d'utilisation](https://github.com/theodubus/memory/blob/13223681bf85ce7b842ee5deb2621736a66f5f1b/engine/socle/HELP.md),
  section « Répondre à l'agent » : il dit déjà que `valider` est la seule
  réponse qui autorise un geste réservé à l'humain. L'option 1 le garde
  tel quel ; l'option 2 le change.

## Options

1. **Le lint exige `valider`.** Une demande qui nomme un test du projet ou
   une clé des seuils, c'est-à-dire ce que lisent les deux contrôles qui
   acceptent une validation, doit offrir `valider` parmi ses réponses ;
   sinon le lint la refuse, avant que l'humain ne la lise. Une demande de
   choix entre plusieurs gestes s'écrit alors avec `valider` pour l'option
   recommandée, et les autres options mènent à une demande nouvelle. Effort :
   une à deux heures, avec le défaut injecté dans l'auto-test. Risque
   faible : la règle « seul `valider` valide » ne change pas, le lint lit
   les mêmes noms que les contrôles. Réversible : un contrôle qui se
   retire.
2. **La demande déclare ses réponses qui valident.** Une réponse marquée
   (par exemple `- \`tout\` — … (valide)`) compte comme `valider`. Effort :
   une demi-journée : le modèle des demandes, le format, le guide et ses
   tests. Risque moyen : ce qui autorise l'agent s'élargit, et une réponse
   partielle (`compatibilite-seule`) autoriserait tous les tests que la
   demande nomme, y compris ceux que seule l'autre option touchait, sauf à
   attacher à chaque option ses propres tests. Réversible, mais les
   demandes répondues entre-temps garderaient leur sens.
3. **Rien dans l'outil.** La règle s'écrit dans les instructions de
   l'agent (« une demande qui autorise un geste offre `valider` »), sans
   contrôle. Effort : quelques minutes. Risque : la faute peut se
   reproduire, et ce dépôt veut qu'un garde-fou ait été vu échouer.
   Réversible.

## Conséquences

- Si Théo valide (option 1) : le lint est écrit, avec son défaut injecté et
  un témoin sain ; B-0081 est clos. Les demandes déjà répondues ne changent
  pas.
- S'il choisit `declarer` (option 2) : le format des demandes et le guide
  changent, et chaque option porte la liste de ce qu'elle autorise.
- S'il choisit `instructions` (option 3) ou refuse : seule la consigne
  s'écrit, ou rien ; B-0081 reste ouvert ou est clos sans correctif.
- Sans réponse : rien ne change ; la prochaine demande qui autorise un
  geste est rédigée avec `valider`, comme D-0035.

## Recommandation

L'option 1.

Vérifié : la réponse `tout` n'a débloqué aucun test (il a fallu D-0035) ;
`Demande.validee` ne compare la réponse qu'à `valider` ; le contrôle des
tests protégés cherche le nom du test, en mot entier, dans le texte des
demandes validées, et le cliquet y cherche la clé du seuil.

Supposé : que lire les noms des tests et des clés dans le lint coûte ce
que coûtent déjà les deux contrôles, et qu'une demande qui choisit entre
plusieurs gestes autorisés reste rare, si bien que la seconde demande de
l'option 1 coûte peu.

## Réponses possibles

- `valider` — option 1 : le lint refuse une demande qui nomme un test ou une clé des seuils sans offrir `valider`.
- `declarer` — option 2 : une demande déclare celles de ses réponses qui valident, chacune avec ce qu'elle autorise.
- `instructions` — option 3 : la règle s'écrit dans les instructions de l'agent, sans contrôle.
- `refuser` — rien ne change ; B-0081 est clos sans correctif.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
