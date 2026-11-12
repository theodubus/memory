<!-- socle: couche=demandes zone=publique -->
# D-0104 — Autoriser le changement de deux valeurs attendues d'un test du mode adoption, pour que la clé d'un constat toléré dise la classe du test et le paragraphe recopié

> date : 2026-11-12

## Décision demandée

Autoriser l'agent à changer deux valeurs attendues du test `test_les_controles_d_adoption_citent_leur_objet` (`tests/test_adoption.py`), pour que la clé d'un constat toléré par l'adoption nomme la classe du test fautif et le paragraphe recopié.

## Contexte

**Le projet.** Le socle est un moteur de contrôles pour les projets de code qu'un agent entretient : il vérifie la mémoire, la documentation et les tests d'un projet, avant chaque commit et dans son intégration continue. Théo le fabrique dans ce dépôt, et l'a installé le 12 novembre sur chess, son moteur d'échecs.

**Le chantier.** L'installation sur chess a montré un défaut du mode adoption. Ce mode sert à équiper un projet qui existe déjà : les défauts trouvés à l'installation, appelés constats, y restent de simples avertissements, le temps de les résorber. Or il désarmait le contrôle entier, constats nouveaux compris. Depuis le lot du 12 novembre, il ne tolère plus que les constats présents à l'installation, que l'installeur inscrit un par un dans les réglages protégés du projet (`.socle/guardrails.toml`) ; tout constat nouveau fait échouer son contrôle. Ce lot est poussé sur la pull request 37, que l'agent fusionnera quand ses dernières corrections seront faites, sans doute aujourd'hui.

**La question.** Chaque constat toléré est inscrit sous une clé : son fichier, puis l'objet fautif. Pour deux contrôles, cette clé est trop pauvre, et la corriger change deux valeurs qu'un test déjà poussé attend. La politique du projet réserve ce geste à l'humain, Théo : un agent qui changerait seul une valeur attendue pourrait affaiblir un test pour le faire passer.

Le défaut. Deux constats différents peuvent avoir la même clé ; un constat neuf prend alors la place d'un ancien qu'on vient de corriger, et passe en avertissement au lieu d'échouer.

- Le contrôle des tests creux, qui refuse un test sans assertion, inscrit « sans assertion test_rien », sans la classe du test. Deux tests de même nom, dans deux classes d'un même fichier, ont la même clé.
- Le contrôle des copies, qui refuse un paragraphe recopié tel quel dans deux fichiers, inscrit « copie en b.md », sans dire quel paragraphe. Un autre paragraphe recopié entre les deux mêmes fichiers a la même clé.

Le cas est étroit : il faut corriger un constat ancien et en créer un nouveau de même clé, dans le même fichier. Le nombre de constats tolérés ne monte jamais.

D'où vient ce constat. Avant d'être poussé, chaque lot est relu par un autre agent, qui n'a pas le contexte et cherche les défauts : une revue. Cette règle en a eu deux. La seconde a rendu six constats ; le troisième dit que la clé ne distingue plus assez les fautes. Pour un autre contrôle, celui des références, le relecteur l'a reproduit : un lien mort et un chemin cité inexistant vers la même cible avaient la même clé. Ce cas-là est corrigé sans toucher à une valeur attendue. Les deux cas de cette demande ne peuvent pas l'être ainsi.

Le changement. La ligne 98 du test attend aujourd'hui :

    {"tests.creux": "sans assertion test_rien", "docs.copie": "copie en b.md"}

Elle attendrait :

    {"tests.creux": "sans assertion T.test_rien", "docs.copie": "copie en b.md : Un long paragraphe recopié tel quel dans deux"}

« T » est la classe du test de l'exemple ; la clé d'une copie porterait les huit premiers mots du paragraphe. Deux paragraphes qui commencent par les mêmes huit mots se confondraient encore. Aucune autre valeur attendue ne change, aucun test n'est supprimé, et le test reste aussi strict : il attend toujours une valeur exacte, plus précise qu'avant. L'agent ajoutera un test par cas, qui échoue avant le changement.

Pourquoi maintenant. Aucun projet n'a encore de liste écrite avec ces clés : le lot n'est ni fusionné, ni publié dans le dépôt public d'où les projets reçoivent le socle. chess n'a donc pas reçu la mise à jour ; il a aujourd'hui deux constats du contrôle des tests creux, deux assertions jugées vides de sens, et aucun du contrôle des copies. Changer la forme d'une clé plus tard ferait redevenir des erreurs les constats déjà inscrits sous l'ancienne forme, sur chaque projet adopté.

## Éléments cités

- ADR-0068@c9c2cfbd — la décision du 12 novembre : l'adoption ne tolère que les constats présents à l'installation, inscrits sous une clé faite du fichier et de l'objet fautif.
- B-0180@fe4775a9 — le sujet clos qui a livré cette règle, parti du constat fait sur chess.
- B-0189@7a010dd2 — le sujet en cours : les six constats de la seconde revue de cette règle, dont celui-ci.
- ADR-0017@4ce8d68e — la décision qui réserve à l'humain le changement d'une valeur attendue dans un test.
- pull request 37 — la pull request ouverte de ce dépôt ; elle porte la règle de l'adoption et cinq autres petites corrections venues de l'installation sur chess.

## Où regarder

- [tests/test_adoption.py, lignes 87 à 98](https://github.com/theodubus/memory/blob/8486be4dc46c54dc699e403aa7f954c5689b8d2b/tests/test_adoption.py#L87-L98) — le test ; la ligne 98 porte les deux valeurs, recopiées plus haut.
- [La décision sur l'adoption](https://github.com/theodubus/memory/blob/8486be4dc46c54dc699e403aa7f954c5689b8d2b/memory/decisions/ADR-0068-l-adoption-tolere-les-constats-presents-a-l-instal.md) — la règle, et la forme d'une clé.
- [Le sujet de la seconde revue](https://github.com/theodubus/memory/blob/8486be4dc46c54dc699e403aa7f954c5689b8d2b/memory/backlog/B-0189-seconde-revue-de-b-0180-un-fichier-renomme-perd-sa.md) — les six constats ; le troisième est celui-ci.

## Options

1. Valider. Les deux clés deviennent plus précises. Effort : moins d'une heure d'un agent auxiliaire, dans le lot en cours. Risque : faible. Pour les copies, la clé dépend du début du paragraphe : si l'on retouche les huit premiers mots d'un paragraphe recopié et toléré, son constat redevient une erreur. L'issue normale est alors de supprimer la copie ; sinon, réinscrire le constat dans la liste assouplit un garde-fou, ce qui demande l'accord de Théo. Le cas devrait être rare : il ne touche que les paragraphes recopiés déjà tolérés. Réversibilité : entière tant que rien n'est publié ; ensuite, changer la forme d'une clé coûte une migration des listes sur chaque projet adopté.
2. Refuser. Les clés restent telles quelles. Effort : aucun. Risque : le cas étroit décrit plus haut reste possible, pour les tests sans assertion et pour les copies ; il sera écrit comme une limite connue dans la décision du lot en cours. Réversibilité : on peut valider plus tard, au prix de la migration.

Pour n'autoriser qu'un des deux changements, refuser en le disant : l'agent reposera une demande plus étroite.

## Conséquences

- Si tu valides : l'agent change la ligne 98 du test et les deux contrôles, dans le lot en cours, avant la fusion de la pull request 37 et avant la mise à jour de chess.
- Si tu refuses : rien ne change. La limite est écrite, et la pull request 37 se fusionne sans ce changement.
- Sans réponse : l'agent ne touche pas à ce test. Il attend ta réponse jusqu'à ce que le reste du lot soit prêt, puis fusionne la pull request 37 sans ce changement ; valider ensuite coûtera une migration des listes déjà écrites.

## Recommandation

Valider, pour les deux contrôles : c'est le moment où cela ne coûte rien.

Vérifié : le test et ses deux valeurs attendues, lus à la ligne 98 ; le même défaut pour le contrôle des références, reproduit par le relecteur, puis corrigé sans toucher à une valeur attendue.

Supposé : les deux cas de cette demande, que le relecteur a lus dans le code sans les reproduire, et qu'un test nouveau établira avant le changement ; le coût d'une migration plus tard, qui n'a pas été mesuré.

## Réponses possibles

- `valider` — l'agent change les deux valeurs attendues de ce test et les deux clés, dans le lot en cours.
- `refuser` — rien ne change ; la limite reste écrite.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
