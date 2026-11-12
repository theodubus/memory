<!-- socle: couche=decisions zone=publique -->
# ADR-0070 — La clé d'une copie dit les huit premiers mots de son paragraphe ; celle d'un test creux ne dit pas sa classe

> statut : acceptée · date : 2026-11-12 · validation : D-0104@26f570ad · source : B-0190@2aaaf027, ADR-0069@5eb28115, ADR-0068@c9c2cfbd, B-0189@f5fb31de · lu : decisions@c5301446

## Contexte

L'adoption tolère un constat sous la clé `<fichier> — <objet>` (ADR-0068,
amendée par ADR-0069). Pour deux contrôles, l'objet ne distinguait pas
deux fautes d'un même fichier : `tests.creux` citait le test sans sa
classe (`sans assertion test_rien`), `docs.copie` les autres fichiers sans
le paragraphe (`copie en b.md`). Un constat neuf pouvait alors prendre la
place d'un ancien corrigé, et passer en avertissement. Théo a autorisé à
changer les deux valeurs attendues du test qui les fixe (D-0104).

## Décision

Elle amende ADR-0069 sur la clé d'une copie seulement ; le reste tient.

1. L'objet d'un constat de `docs.copie` porte, après les autres fichiers,
   les huit premiers mots du paragraphe recopié, blancs réduits, coupés à
   80 caractères : `copie en b.md : Un long paragraphe recopié tel quel
   dans deux`. Un paragraphe de moins de huit mots les donne tous.
2. L'objet d'un constat de `tests.creux` garde le nom du test seul. Une
   première version y mettait la classe, lue par le mot `class` ; la revue
   du lot (sept constats) l'a écartée. La classe ne se lit pas sûrement par
   une expression régulière dans tous les langages : une classe sans corps
   (`data class P(val x: Int)`, `class A: pass`) avale la suite du fichier,
   une annotation sur sa ligne la cache, `object` et `module` ne sont pas
   lus, et une chaîne de Rust ou de Go peut en simuler une. Une lecture
   fausse change alors la clé de constats tolérés quand on ajoute une ligne
   sans rapport, et les fait redevenir des erreurs : pire que le cas étroit
   à fermer. La limite d'ADR-0069 reste donc pour les tests creux : deux
   tests de même nom dans deux classes d'un fichier ont la même clé.

## Conséquences

Deux paragraphes recopiés entre les deux mêmes fichiers ont deux clés, et
le neuf échoue (`tests/test_adoption.py`, `TestClesDistinctes`). Limites
qui restent : deux paragraphes qui commencent par les mêmes huit mots se
confondent encore ; retoucher le début d'un paragraphe recopié et toléré
change sa clé, et son constat redevient une erreur (supprimer la copie, ou
la réinscrire par une demande validée). Aucune liste n'est encore écrite
sous l'ancienne forme ; défaire cette décision plus tard coûterait une
migration des listes des projets adoptés.
