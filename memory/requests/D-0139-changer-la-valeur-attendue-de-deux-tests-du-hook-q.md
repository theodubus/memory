<!-- socle: couche=demandes zone=publique -->
# D-0139 — Changer la valeur attendue de deux tests du hook que contredisent T-0007 et T-0083 du lot L-0005

> date : 2026-11-19

## Décision demandée

Autoriser l'agent à changer la valeur attendue de deux tests existants, `test_un_diese_et_les_guillemets_d_une_substitution` (`tests/test_garde.py`) et `test_l_ancien_numero_dans_un_texte_neuf_fait_nommer_l_identifiant_actuel` (`tests/test_structure.py`), qui fixent l'ancien comportement que corrigent les tâches T-0007 et T-0083.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet (ses décisions, son journal, son backlog, la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le lot en cours, L-0005, corrige ce que laisse passer le hook de l'agent, le programme qui contrôle chacune de ses commandes et de ses écritures avant qu'elles agissent. Ses sujets sont de priorité haute ; le 16 novembre, vous y avez fait entrer celui de la substitution entre guillemets, et borné le hook aux formes qu'un agent écrit dans son travail, les autres allant à une liste du guide sans être corrigées. Un sous-agent, un autre agent lancé pour implémenter, en a implémenté quatre tâches : deux sont livrées (le hook juge ce que lancent `uv run` et `poetry run`, deux lanceurs de commandes Python, et un `git push` dont la branche ou l'option passe par une variable) ; les deux autres sont prêtes et vérifiées, mais chacune contredit un test qui fixait l'ancien comportement.

**La question.** La politique d'autonomie du projet, que vous seul changez, exige votre accord par une demande validée pour changer la valeur attendue d'un test existant ; une décision écrite par l'agent ne suffit pas. Voici les deux tests, chacun avec sa valeur avant et après.

**Le test de T-0007, la substitution entre guillemets.** Une substitution, `$(…)`, lance une commande et met sa sortie à sa place. Écrite entre guillemets, `x="$(…)"`, une forme courante, le hook ne regarde pas la commande qu'elle lance : `x="$(cd .. && rm -rf projet)"` supprime le projet sans refus. L'agent l'avait laissé en risque accepté le 15 novembre (B-0207), avant votre règle du 16 novembre, qui fait juger les formes qu'un agent écrit, dont celle-ci. T-0007 fait juger cette commande comme celle d'une substitution sans guillemets ; une substitution ordinaire, `x="$(git rev-parse HEAD)"`, passe toujours. Le test `test_un_diese_et_les_guillemets_d_une_substitution` ([`tests/test_garde.py`, ligne 1661](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/tests/test_garde.py#L1661)) vérifie plusieurs découpages d'une ligne de commandes (un dièse, des guillemets), qui ne changent pas ; à la fin, il découpe `X="$(echo "; cd /tmp; ")"; ls` en commandes, chacune avec le dossier où elle s'exécute (vide : le dossier courant), et son commentaire dit : « Ce que lance une substitution entre guillemets ne se juge pas (un risque accepté) ».

- Avant : une seule commande, `ls` : `[(["ls"], "")]`.
- Après : la commande de la substitution, puis `ls` : `[(["echo", "; cd /tmp; "], ""), (["ls"], "")]`. Le `cd` écrit entre les guillemets de l'`echo` reste du texte, pas un changement de dossier : le dossier reste vide. Le commentaire dit alors que la substitution se juge.

**Le test de T-0083, l'ancien numéro repris.** Le 16 novembre, les entrées du backlog ont changé de préfixe : un besoin devenu un lot, par exemple, a pris un numéro nouveau. Le hook refuse alors un texte neuf qui cite l'ancien numéro, et dit le numéro actuel. Mais il sautait toute mention que le fichier portait déjà, comme pour toute référence : c'était voulu, pour ne pas refuser une écriture qui recopie les lignes d'avant (l'agent récrit souvent un fichier entier) ; un ancien numéro se résout partout, et ne trompe pas. L'effet : dans un fichier du journal qui cite un ancien numéro, une ligne neuve qui le reprenait passait. Le 18 novembre, le relecteur sans contexte d'un lot, un agent, l'a relevé : chez chess, le journal du mois de sa mise à jour vers cette version du socle citera presque tous les anciens numéros, et le refus n'y tirerait presque jamais. T-0083 juge l'ancien numéro sur les lignes que l'écriture ajoute ou change ; une ligne recopiée telle quelle, ou qui nomme aussi le numéro actuel, passe toujours. Une ligne neuve refusée se corrige en citant le numéro actuel, que le refus donne. Le test `test_l_ancien_numero_dans_un_texte_neuf_fait_nommer_l_identifiant_actuel` ([`tests/test_structure.py`, ligne 464](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/tests/test_structure.py#L464)) attend exactement l'ancien comportement : sa description dit « Le journal qui le cite déjà se complète sans refus ». Plus bas, `<ancien>` tient la place de l'ancien numéro qu'emploie le test, celui d'un besoin devenu lot dans le projet d'essai qu'il fabrique ; `ecrire(journal, …)` soumet au hook l'écriture du journal, son contenu d'avant suivi de la ligne neuve, et rend le refus, vide s'il n'y en a pas.

- Avant : ajouter « Le lot `<ancien>` avance. » au journal qui cite déjà `<ancien>` ne rend aucun refus : `assertEqual(ecrire(journal, … + "\nLe lot <ancien> avance.\n"), "")`.
- Après : la même écriture est refusée et nomme l'ancien numéro : `assertIn("ancien numéro — <ancien>", ecrire(journal, …))`. La phrase de la description qui disait l'inverse se retire.

Rien d'autre ne change dans ces deux tests ; chaque tâche ajoute ses propres tests, qui échouent sans elle. T-0083 ajoute aussi une décision de conception de l'agent, qui complète ADR-0087 sur ce que le refus arrête désormais ; elle ne touche aucune de vos décisions.

## Éléments cités

`T-`, une tâche, le livrable d'un commit ; `B-`, un besoin, un résultat à atteindre ; `L-`, un lot ; `D-`, une demande comme celle-ci ; `ADR-`, une décision de conception de l'agent ; après @, l'empreinte de la version lue.

- L-0005@e13c9fd7 — le lot en cours, ce que le hook laisse passer, dont ces deux tâches.
- T-0007@9675ab59 — la tâche qui fait juger la commande d'une substitution entre guillemets.
- B-0260@dd8c1330 — le besoin qu'elle sert, de priorité haute : le projet supprimé par une substitution entre guillemets.
- B-0207@854c7a3f — le besoin clos du 15 novembre où l'agent avait laissé ce cas en risque accepté.
- T-0083@ef8b8e4f — la tâche qui juge l'ancien numéro sur les lignes que l'écriture ajoute.
- B-0265@6a1180af — le besoin qu'elle sert, de priorité haute : le vocabulaire du backlog et les anciens numéros de ses entrées.
- T-0051@50994b00 — la tâche close qui a posé le refus de l'ancien numéro, et le test qui change.
- ADR-0087@39a38e17 — la décision qui dit ce que ce refus arrête et laisse passer ; T-0083 la complète.
- D-0120@f10e0e80 — votre accord du 16 novembre qui borne le hook aux formes qu'un agent écrit.

## Où regarder

- [Le test de T-0007](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/tests/test_garde.py#L1661), ses dernières lignes : le commentaire du risque accepté et la valeur attendue.
- [Le test de T-0083](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/tests/test_structure.py#L464), sa description et l'assertion sur le journal, juste avant le commentaire « Une référence inventée ».
- [Le besoin de T-0007](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/memory/backlog/B-0260-le-hook-de-l-agent-ne-juge-jamais-ce-que-lance-une.md) et [la tâche T-0083](https://github.com/theodubus/memory/blob/462cb46d4f258c68172f784a6344e124ea6738d9/memory/backlog/T-0083-le-hook-juge-l-ancien-numero-sur-les-lignes-qu-une.md) : pourquoi chaque changement.

## Options

- Valider : les deux valeurs attendues changent comme dit plus haut, avec T-0007 et T-0083 ; effort faible, les deux tâches sont prêtes et vérifiées ; risque faible : le hook refuse davantage, et seulement des commandes qu'une substitution lance ou un ancien numéro repris ; réversible par une demande nouvelle.
- Refuser : T-0007 et T-0083 s'abandonnent en renvoyant à votre réponse ; `x="$(… rm -rf …)"` et l'ancien numéro repris dans un fichier qui le cite déjà continuent de passer le hook, et leurs besoins restent ouverts au backlog, sans tâche, jusqu'à une autre piste ; effort nul ; réversible.
- N'en valider qu'un : le dire dans votre réponse, en nommant la tâche gardée ; l'agent pose alors une demande pour son seul test, et l'autre tâche s'abandonne.

## Conséquences

Si vous validez : l'agent commite chaque tâche avec son test changé et votre réponse, dans un même push, puis fait relire le lot entier par un relecteur sans contexte, un autre agent chargé de le prendre en défaut, avant de le livrer ; un constat bloquant se corrige dans le lot, et revient à vous par une demande s'il change encore une valeur attendue. Si vous refusez : il livre le lot avec ses deux autres tâches, et les deux besoins restent ouverts. Sans réponse : les deux tâches attendent, et le reste du lot avance.

## Recommandation

Valider. Vérifié : le sous-agent a lancé, avec chaque changement, les tests ciblés du hook ; les tests nouveaux de chaque tâche échouent sans elle ; l'auto-test du socle, qui injecte dans le moteur le défaut que chaque refus doit attraper, l'attrape ; seuls ces deux tests existants changent. Supposé : rien.

## Réponses possibles

- `valider` — les deux valeurs attendues changent, avec T-0007 et T-0083, dans le même push que votre réponse.
- `refuser` — les deux tests restent tels quels, T-0007 et T-0083 s'abandonnent.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
