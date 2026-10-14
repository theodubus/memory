<!-- socle: couche=demandes zone=publique -->
# D-0025 — Faire tourner sur GitHub la CI que posent les cinq nouveaux adaptateurs, dans un dépôt jetable que tu crées

> date : 2026-10-14 · lu : decisions@c92d474a

## Décision demandée

Choisir si tu crées sur GitHub un dépôt jetable où je pousse un petit
projet de chaque langage (JavaScript, Go, Java, Ruby, PHP), pour vérifier
que la CI que le socle pose dans un tel projet tourne vraiment.

## Contexte

Le socle s'installe dans un projet de code et y pose sa CI GitHub : un
workflow qui installe les outils du langage, puis lance les contrôles du
socle. Les cinq adaptateurs ajoutés le 11 oct. (JavaScript et TypeScript,
Go, Java, Ruby, PHP) apportent chacun leurs étapes d'installation dans ce
workflow : Node et `npm ci`, Go, Java et Maven, Ruby et Bundler, PHP avec
son pilote de couverture. Le banc des adaptateurs a éprouvé chaque
adaptateur sur un projet jetable de son langage, mais dans ce conteneur,
avec les outils déjà là ; les étapes d'installation de la CI, elles, n'ont
jamais tourné sur GitHub. Elles sont supposées justes. Si l'une est
fausse, quelqu'un qui installe le socle sur un projet de ce langage a une
CI rouge dès son premier push, sans que rien ici ne l'ait vu.

Pour les éprouver, il faut un dépôt GitHub où pousser ces projets. Je ne
peux pas en créer : la création d'un dépôt est une action externe, que le
hook me refuse (politique, point 4), et ma session n'a accès qu'au dépôt
`theodubus/memory`. Un seul dépôt suffit : chaque projet va sur sa propre
branche, et la CI tourne à chaque push de branche. Le banc sait garder ses
projets jetables (`--garder`) pour que je les pousse tels quels.

## Éléments cités

- B-0039@55928fbb — le sujet du backlog qui demande d'éprouver ces étapes
  de CI sur GitHub, ouvert quand les cinq adaptateurs ont été ajoutés.
- F-0018@1013e747 — le fait mesuré : les cinq adaptateurs passent les
  douze étapes de leur banc, dans ce conteneur et pas sur GitHub.
- ADR-0021@d84f5620 — la décision qui a ajouté les cinq adaptateurs, chacun
  avec l'outil de tests et de mutation le plus courant de son langage.

## Où regarder

- [le sujet B-0039](https://github.com/theodubus/memory/blob/430d56fd7b3d717e30687c7c87f4463163f3aef9/memory/backlog/B-0039-eprouver-sur-github-les-etapes-de-ci-que-posent-le.md) :
  ce qui reste supposé.
- [les étapes de CI de l'adaptateur JavaScript](https://github.com/theodubus/memory/blob/430d56fd7b3d717e30687c7c87f4463163f3aef9/engine/socle/adapters/javascript.toml#L17-L23) :
  un exemple de ce que chaque adaptateur ajoute au workflow, et qui n'a
  jamais tourné sur GitHub.
- [le workflow que pose l'installeur](https://github.com/theodubus/memory/blob/430d56fd7b3d717e30687c7c87f4463163f3aef9/engine/socle/templates/socle.yml) :
  où ces étapes s'insèrent.
- [le rapport du banc des adaptateurs](https://github.com/theodubus/memory/blob/430d56fd7b3d717e30687c7c87f4463163f3aef9/bench/reports/2026-10-11-adaptateurs.md) :
  ce qui a été mesuré ici, 60 étapes sur 60.

À vérifier : que tu acceptes un dépôt de plus sur ton compte, le temps de
l'essai, et s'il peut être public.

## Options

- **Un dépôt jetable public, cinq branches** : tu crées un dépôt vide
  (par exemple `theodubus/socle-essai-adaptateurs`) et tu l'ajoutes à ma
  session ; j'y pousse un projet par branche et je lis chaque CI. Effort
  pour toi : deux minutes, puis supprimer le dépôt à la fin. Risque
  faible : les projets ne contiennent qu'un petit module de calcul et ses
  tests, rien du projet. Les minutes de CI d'un dépôt public sont
  gratuites. Réversible : supprimer le dépôt efface tout.
- **Le même, en privé** : mêmes gestes, mais les minutes de CI comptent
  dans ton quota gratuit, environ 25 minutes pour cinq passages. Risque
  faible ; réversible.
- **Ne pas éprouver** : les étapes restent supposées, et B-0039 reste
  ouvert ; effort nul ; risque moyen : une CI rouge au premier push d'un
  projet de l'un de ces langages ; réversible.

## Conséquences

- Si tu valides : dès que le dépôt existe et que ma session y a accès, je
  pousse les cinq projets, je lis chaque CI, je corrige les étapes fausses
  dans les adaptateurs, et je te dis quand tu peux supprimer le dépôt.
- Si tu refuses : B-0039 reste ouvert, avec cette raison, et je passe au
  sujet suivant de l'ordre que tu as validé (une action validée par une
  demande, que le hook refuse encore).
- Sans réponse : je continue le sujet en cours (les sessions de l'agent
  ouvertes hors de la racine du projet) ; la demande reste en file.

## Recommandation

Le dépôt public. Vérifié : chaque adaptateur passe son banc ici, et ses
étapes de CI sont écrites dans son fichier sans avoir jamais tourné sur
GitHub. Supposé : que les actions d'installation qu'elles utilisent
(setup-node, setup-go, setup-java, setup-ruby, setup-php) se comportent
sur GitHub comme ces étapes l'attendent, et qu'un passage dure environ
cinq minutes.

## Réponses possibles

- `public` — tu crées un dépôt jetable public et tu me le donnes ; j'y pousse les cinq projets.
- `prive` — le même, en privé.
- `refuser` — on n'éprouve pas ces étapes ; B-0039 reste ouvert.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
