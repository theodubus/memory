<!-- socle: couche=demandes zone=publique -->
# D-0242 — Chess garde désormais 10 000 octets pour ses skills : supprimer le test TestLePlafondDesProjetsInstalles, qui garde les skills du produit sous 8 000 octets pour lui ?

> date : 2026-11-28

## Décision demandée

Supprimer de `tests/test_skills.py` la classe de test `TestLePlafondDesProjetsInstalles` et sa fonction `test_chaque_skill_pose_tient_sous_8000_octets`, puisque chess en garde désormais 10 000 octets pour ses skills, et que JustCook, l'autre projet installé, posera la même demande à sa mise à jour, avant d'en commiter les fichiers.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, le moteur que reçoit un projet confié à un agent d'IA pour qu'il garde sa mémoire, vérifie son travail et ne te sollicite que pour les vraies décisions ; chess et JustCook sont les deux projets réels qui l'ont installé.

**Le chantier.** Le 26 novembre, tu as choisi de relever de 8 000 à 10 000 octets le plafond de taille des skills (les procédures que l'agent charge en entier), ici et dans le gabarit des garde-fous, en disant que chaque projet installé validerait la même valeur à sa mise à jour. Une mise à jour garde les garde-fous du projet : un projet installé avant reste à 8 000. Le 27 novembre, un test a été ajouté pour que les skills que pose l'installeur tiennent sous ces 8 000 octets, faute de quoi le commit de la mise à jour de chess aurait été refusé ; et tu as validé que le prompt de mise à jour fasse poser à chess la demande des 10 000 octets, puis que tu dises, chess à 10 000, ce que devient ce test.

**La question.** Chess a été mis à jour le 28 novembre : sa demande, qui nommait la clé, a été validée, et 10 000 octets sont posés dans la même pull request, dont les deux CI sont vertes. Reste JustCook, le pilote installé le 31 octobre, que tu as gardé pour après la mise à jour de chess : son gabarit d'alors posait 8 000 octets.

Le test vérifie que chaque gabarit de skill du produit, en français et en anglais, fait au plus 8 000 octets. D'autres tests de `tests/test_skills.py` gardent déjà chaque skill sous 10 000 octets dans les deux langues. Les skills les plus longs font entre 7 600 et 7 960 octets : la prochaine règle ajoutée à l'un d'eux, celle par exemple de la clôture d'un besoin sans tâche qui vient du retour de chess, peut dépasser 8 000 et obliger à resserrer le skill, comme le 27 novembre. Sans ce test, JustCook devra, à sa mise à jour, poser la demande des 10 000 octets et la voir validée avant de commiter les fichiers ; sinon son hook avant commit refusera le skill trop long, sans rien perdre : la demande se pose alors.

## Éléments cités

- B-0385@d7f2f023 — le besoin de l'atelier qui fait passer chess à 10 000 octets et attend ta parole sur ce test.
- B-0384@b3af0c41 — le besoin clos qui a posé le test, pour un projet installé avant le 27 novembre.
- B-0104@dcfc609f — le pilote neuf, JustCook, repris après le jalon de la mise à jour de chess.
- D-0223@40c79bfe — ta décision du 26 novembre qui relève le plafond des skills à 10 000 octets.
- D-0241@2d0c2107 — ta décision du 27 novembre : chess pose la demande, puis tu dis ce que devient le test.

## Où regarder

- Le test, à la fin du fichier : [tests/test_skills.py](https://github.com/theodubus/memory/blob/57cfd7c1987767bce7fbe8e82eb951fe312f5743/tests/test_skills.py#L1583) ; vérifier qu'il ne garde que 8 000 octets, pour un projet installé avant le 27 novembre.
- Le retour de chess, sa ligne « Le plafond des skills » : [docs/fabrication/chess/mise-a-jour-2026-11-28.md](https://github.com/theodubus/memory/blob/ccr-bcaf08f9-6fjm2u/docs/fabrication/chess/mise-a-jour-2026-11-28.md).

## Options

- **Supprimer le test, et noter dans B-0104 l'ordre de la mise à jour de JustCook** (ma recommandation). Effort : quelques lignes ôtées, une ligne écrite. Risque : un oubli à la mise à jour de JustCook se voit aussitôt, par un refus de son hook avant commit, et se répare par la demande. Réversible.
- **Garder le test jusqu'à ce que JustCook soit à 10 000, puis le supprimer.** Effort : nul aujourd'hui. Risque : toute règle ajoutée d'ici là à un skill proche du plafond oblige à le resserrer, l'option que tu n'avais pas choisie le 26 novembre. Réversible.
- **Le passer à 10 000 octets.** Effort : une valeur changée. Risque : aucun, mais il doublerait les tests qui gardent déjà ce plafond. Réversible.

## Conséquences

- Si tu valides : le test disparaît dans le prochain lot qui touche les skills ou les tests ; B-0104 dit que la mise à jour de JustCook pose la demande des 10 000 octets avant de commiter ses fichiers ; B-0385 se clôt.
- Si tu refuses : le test reste à 8 000 octets jusqu'à ta prochaine parole, et B-0385 se clôt sur ta réponse.
- Sans réponse : le test reste, et B-0385 attend, avec le jalon de la mise à jour de chess.

## Recommandation

Supprimer le test. Vérifié : chess a validé 10 000 octets le 28 novembre, selon son retour ; d'autres tests du fichier gardent chaque skill sous 10 000 octets dans les deux langues ; les skills du produit font au plus 7 959 octets ; le gabarit des garde-fous posait 8 000 octets le 31 octobre, jour de l'installation de JustCook. Supposé : JustCook garde cette valeur, ce dépôt ne le lisant pas.

## Réponses possibles

- `valider` — le test `TestLePlafondDesProjetsInstalles.test_chaque_skill_pose_tient_sous_8000_octets` est supprimé ; B-0104 note l'ordre de la mise à jour de JustCook ; B-0385 se clôt.
- `refuser` — le test reste à 8 000 octets, B-0385 se clôt sur ta réponse.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
