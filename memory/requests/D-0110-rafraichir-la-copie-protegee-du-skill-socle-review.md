<!-- socle: couche=demandes zone=publique -->
# D-0110 — Rafraîchir la copie protégée du skill socle-review depuis son gabarit : la revue jugée contre le critère et le modèle de menace

> date : 2026-11-14

## Décision demandée

Autoriser l'agent à remplacer la copie du skill `socle-review` que ce dépôt utilise, un fichier protégé, par le texte de son gabarit, que le moteur installe désormais dans tout projet.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le moteur est ce qu'un projet reçoit à l'installation ; ce dépôt s'en sert lui-même, comme premier projet équipé.

**Le chantier.** L'agent travaille par lots : quelques sujets du backlog (la liste des sujets à traiter), livrés ensemble. Avant de livrer un lot, il le fait relire par un relecteur, un autre agent sans son contexte, qui cherche à le prendre en défaut. Le 13 novembre, vous avez demandé que cette revue cesse de s'éterniser : le lot précédent avait pris quatre revues et trois corrections pour deux sujets.

**La question.** Un skill est une procédure écrite que l'agent charge quand il en a besoin. Le socle pose les siens dans chaque projet sous forme de copies protégées, que l'agent ne peut modifier sans votre accord. Le gabarit de ce skill a changé dans le moteur ; la copie de ce dépôt dit encore l'ancienne règle, et contredit la procédure des lots de ce dépôt, qui suit déjà la nouvelle.

Ce que vous avez validé le 13 novembre : la revue juge le lot contre le critère « Fait quand » de ses sujets (les cases à cocher qui disent quand un sujet est fait) et, pour un garde-fou (un contrôle ou un refus automatique qui arrête une faute de l'agent), contre son modèle de menace (ce que le garde-fou arrête, ce qu'il laisse passer), écrit avant son code ; un constat ne se corrige dans le lot que s'il contredit ce critère, fait régresser ce qui marchait ou fait perdre des données ; le reste va au backlog.

Ce que l'agent a ajouté en l'écrivant, dans sa décision ADR-0073 : est aussi bloquant un constat qui contredit une décision citée, ou qui contourne le garde-fou dans son modèle de menace ; un sujet dont la conception n'est pas tranchée écrit sa spécification (ce qu'il fera, décidé et écrit) avant son code ; les constats infondés s'écartent en une ligne, et le récap compte chaque sorte ; la seconde revue change, comme suit.

| | Copie actuelle | Gabarit nouveau |
| --- | --- | --- |
| Seconde revue | « Une seule passe par lot : pas de seconde revue après les corrections. » | « Une passe par lot ; une seconde seulement si la correction des constats bloquants est lourde (elle change la conception d'une partie, pas quelques lignes), et sur elle seule. » |
| Constats | « Corriger chaque constat fondé, dans le lot, avant le push. » | bloquants corrigés dans le lot ; les autres au backlog ; infondés écartés |

Sur la seconde revue, la copie actuelle était déjà contredite par la procédure des lots, qui faisait relire une seconde fois le lot entier après une correction lourde : c'est ainsi que le lot précédent a pris quatre revues. Le gabarit admet une seconde revue, mais sur la seule correction, et c'est l'agent qui juge la correction lourde.

## Éléments cités

- `.claude/skills/socle-review/SKILL.md` `sha256:597fe4b0ce00620e`
- ADR-0073@1e48220c — la décision, écrite par l'agent, qui spécifie cette revue ; le suffixe après @ est l'empreinte de la version lue.
- B-0209@7fa5ad87 — le sujet ouvert le 13 novembre sur votre accord, fait par ce lot.
- D-0103@271de17d — votre accord du 11 novembre, qui avait rafraîchi cette même copie à son texte actuel.
- B-0212@cd7592cd — sujet ouvert par la revue : la revue d'un lot déjà poussé n'a plus ni diff ni sujets.
- B-0213@3cbbe6e6 — sujet ouvert par la revue : la plage de changements que juge le dossier du relecteur.
- B-0214@21e7e2d8 — sujet ouvert par la revue : des restes de texte et de test, en priorité basse.

L'empreinte de la première ligne est celle que la copie aura après remplacement, identique à celle du gabarit : votre accord porte sur ce texte exact.

## Où regarder

- [Le gabarit, le texte nouveau](https://github.com/theodubus/memory/blob/49e785464a0e22c140cd2aa10eda70de04013eae/engine/socle/templates/skills/socle-review/SKILL.md) : les sections « Quand » et « Les constats ».
- [La copie actuelle, à remplacer](https://github.com/theodubus/memory/blob/49e785464a0e22c140cd2aa10eda70de04013eae/.claude/skills/socle-review/SKILL.md).
- [La procédure des lots de ce dépôt](https://github.com/theodubus/memory/blob/49e785464a0e22c140cd2aa10eda70de04013eae/.claude/skills/delegate-lot/SKILL.md), un skill propre à ce dépôt, non protégé, que l'agent a mis à la nouvelle règle dans ce lot : la section « La revue, avant tout push ».
- [La décision ADR-0073](https://github.com/theodubus/memory/blob/49e785464a0e22c140cd2aa10eda70de04013eae/memory/decisions/ADR-0073-la-revue-juge-le-lot-contre-le-critere-et-le-model.md), pour le détail de ce que l'agent a ajouté.

## Options

- Rafraîchir la copie : un fichier recopié du gabarit, octet pour octet ; effort nul, risque faible, réversible en reprenant le texte d'avant sur une nouvelle demande.
- La laisser en retard : aucun effort ; une session qui lirait cette copie plutôt que la procédure des lots corrigerait dans le lot des constats qui ne bloquent pas, ce que vous avez voulu arrêter.

## Conséquences

Si vous validez : l'agent recopie le gabarit dans la copie, et pousse votre réponse avec ce changement, dans le même push. Si vous refusez : la copie garde l'ancienne règle ; le gabarit, lui, reste celui que le moteur installe dans les autres projets, chess compris à sa prochaine mise à jour, et l'agent ouvre un sujet pour réconcilier les deux textes de ce dépôt. Sans réponse : rien ne change, et l'agent continue les autres sujets.

Valider ne vaut que pour la recopie. Les ajouts de l'agent se discutent à part : les refuser se fait par une réponse dans la conversation, qui deviendra une décision nouvelle.

## Recommandation

Valider. Vérifié : le gabarit est le texte que le moteur installe ; l'empreinte citée est celle de ce gabarit ; la copie actuelle est encore celle que vous aviez approuvée le 11 novembre ; les tests du lot passent ; la CI, qui rejoue tous les contrôles sur GitHub, est passée sur le lot avant la correction de son constat bloquant, et juge cette correction à son push. Supposé : que les deux textes en désaccord égareraient une session ; aucune ne s'y est encore trouvée.

## Réponses possibles

- `valider` — l'agent remplace la copie par le gabarit, et pousse votre réponse avec ce changement.
- `refuser` — la copie garde l'ancienne règle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
