<!-- socle: couche=demandes zone=publique -->
# D-0020 — Passer les installations neuves au format 3, le backlog en un fichier par sujet

> date : 2026-10-13 · lu : decisions@a1a1eb4f

## Décision demandée

Changer la valeur attendue d'un test : qu'une installation neuve pose la
mémoire au format 3, le backlog en un fichier par sujet, au lieu du
format 2.

## Contexte

Tu as validé le backlog en un fichier par sujet, avec une migration
scriptée pour les projets déjà installés. Le moteur lit, écrit et migre
maintenant ce format, qu'on appelle le format 3, et ce dépôt y est passé :
ses 33 sujets ont chacun leur fichier. Reste à en faire le format d'une
installation neuve : une constante du moteur, et un test qui fixe
aujourd'hui qu'un projet neuf est au format 2. Changer ce qu'un test
affirme demande ta validation (politique, point 2) : ta validation du
format ne nomme pas ce test. J'ai fait la bascule sur une copie de l'arbre
et lancé toute la suite : 463 tests, un seul échec, celui-là. Les autres
tests qui portaient sur le backlog en un seul fichier installent
maintenant leur projet au format 2 explicitement, sans rien changer à ce
qu'ils affirment, et le format 3 a ses propres tests.

## Éléments cités

- **Ta validation du backlog en un fichier par sujet** (D-0017@22c858f3) :
  un dossier, son pendant privé, plus d'archivage au journal, un plafond
  par sujet, une migration pour les projets installés.
- **La décision qui décrit ce format** (ADR-0025@f97acbb5) : le nom des
  fichiers, ce qui devient d'un sujet clos, du plafond, de la bascule en
  privé, des liens écrits vers l'ancien fichier unique.
- **Le test qui changerait** : `test_un_projet_neuf_est_au_format_2`, dans
  `tests/test_formats.py`. Il installe le socle dans un dépôt neuf et
  affirme que le format détecté est le 2 ; il deviendrait
  `test_un_projet_neuf_est_au_format_3`, et affirmerait le 3. Ses autres
  vérifications (le verrou, la mémoire, les chemins de la zone privée) ne
  changent pas.

## Où regarder

- [le test, dans `tests/test_formats.py`](https://github.com/theodubus/memory/blob/d2592fbfa59ebeeba7770f118632f80f77887662/tests/test_formats.py#L117) :
  la ligne qui affirme le format 2 d'un projet neuf.
- [la décision sur le format 3](https://github.com/theodubus/memory/blob/d2592fbfa59ebeeba7770f118632f80f77887662/memory/decisions/ADR-0025-le-backlog-un-fichier-par-sujet-format-3.md) :
  vérifier qu'elle dit ce que tu as validé.
- [l'entrée de journal qui raconte le travail](https://github.com/theodubus/memory/blob/d2592fbfa59ebeeba7770f118632f80f77887662/memory/journal/2026-10-2.md#j-2026-10-13-r--b-0047-et-b-0053--le-format-3-se-lit-s%C3%A9crit-et-se-migre--ce-d%C3%A9p%C3%B4t-y-passe) :
  ce qui est fait, et pourquoi les installations neuves attendent.
- [la constante du format d'une installation neuve](https://github.com/theodubus/memory/blob/d2592fbfa59ebeeba7770f118632f80f77887662/moteur/socle/config.py#L83) :
  ce qui passerait de 2 à 3.

## Options

- **Valider** : le test affirme le format 3 sous son nouveau nom, la
  constante passe à 3, et une mise à jour migre un projet au format 2
  vers le 3. Effort faible, une heure avec la vérification ; risque faible,
  mesuré par l'essai ; réversible en remettant la constante et le test.
- **Refuser** : les installations neuves restent au format 2 ; le format 3
  se lit toujours, mais aucune mise à jour n'y mène. Effort nul ; deux
  formes du backlog coexistent sans fin.

## Conséquences

- Si tu valides : je fais la bascule, la CI vérifie tout, et le sujet du
  backlog en un fichier par sujet se clôt.
- Si tu refuses : rien ne change pour les installations ; ce dépôt reste
  au format 3, que le moteur lit.
- Sans réponse : rien ne change ; je travaille sur autre chose.

## Recommandation

Valider. Vérifié : l'essai de la bascule sur une copie de l'arbre, 463
tests dont un seul échoue, celui-ci ; la migration éprouvée sur ce dépôt et
par ses tests. Supposé : qu'aucun projet installé, hors ce dépôt et la
copie du projet d'échecs, n'a à migrer.

## Réponses possibles

- `valider` — la constante passe à 3 et le test affirme le format 3 d'un projet neuf.
- `refuser` — les installations neuves restent au format 2.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
