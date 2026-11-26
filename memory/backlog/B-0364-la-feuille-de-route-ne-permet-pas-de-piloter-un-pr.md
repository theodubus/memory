<!-- socle: couche=backlog zone=publique -->
# B-0364 — La feuille de route ne permet pas de piloter un projet : illisible au format détaillé, elle ne dit pas ses étapes en clair, et la section installée en fige le format

> statut : ouvert · origine : J-2026-11-26-AB · lu : backlog@993edac6 · ref : D-0212

Théo, le 26 novembre (J-2026-11-26-AB), sur la feuille de route que la
session de chess lui a donnée au format détaillé : « La roadmap format
long markdown est illisible et ne permet pas de se projeter ni de
piloter correctement le projet » ; « En soit nous là on fait des
corrections pour adopter la mise a jour, ensuite on repasse aux
optimisations, et on a une liste d'étapes et itérations a faire
(réseaux, spsa etc) et ça franchement c'est pas limpide en lisant
rapidement ».

Ce que montre la sortie de chess : des tableaux que l'application
mobile défait cellule par cellule, une légende de huit symboles, des
identifiants partout et des titres coupés ; le travail en cours, hors
de tout jalon, passe avant les étapes ; les jalons ne sont dits que par
des listes d'identifiants ; un même besoin paraît deux ou trois fois.
Seul le paragraphe « En clair », écrit par l'agent, disait la suite.

S'y joint le point 3 du retour d'usage de chess
(`docs/fabrication/chess/usage-2026-11-26.md`) : la section du socle
installée dit de coller la sortie de `socle roadmap --format markdown`,
quand la consigne de chess demande le format court ; FORMAT.md prend ce
cas pour exemple de consigne.

La conception n'est pas tranchée : sa question d'intention est posée à
Théo le 26 novembre, une maquette sur les données de chess à l'appui ;
la spécification et le code suivent sa réponse, dans un même lot.

Le même jour, Théo valide que la forme retenue remplace les deux
formats actuels, partout (D-0212) ; la forme reste à choisir parmi trois
maquettes fictives, `docs/fabrication/maquettes-feuille-de-route.md`
(J-2026-11-26-AC).

## Satisfait quand

- [ ] lue sur un téléphone, la feuille de route d'un projet dit en clair ses étapes dans l'ordre, où en est chacune et ce qui vient ensuite, sans tableau ni légende
- [ ] la section du socle installée ne fixe plus un format de la feuille de route que les consignes d'un projet contredisent
