<!-- socle: couche=backlog zone=publique -->
# B-0313 — Une décision donnée sans question autorise ce que son titre, écrit par l'agent, nomme seul : un test, une clé des garde-fous ou un fichier que le texte de l'humain ne nomme pas

> statut : ouvert · origine : J-2026-11-20-AC · lu : backlog@24fe7682

Relevé par la passe 1 de la revue de L-0006 (J-2026-11-20-AC). Une
décision que l'humain donne de lui-même (`socle decision --unprompted`,
T-0017) est validée, et les contrôles qui cherchent une validation
(`tests.attendus` par `_justifie`, `cliquet.garde-fous` et
`protege.fichiers` par `_valide_par`, `demandes.reponse-seule`) la
lisent sur son texte entier, titre compris. Le titre est de l'agent ;
`titre_sans_preuve` n'y juge que les identifiants. Un nom de test, une
clé ou un chemin que le titre nomme seul est donc autorisé sans que
l'humain l'ait lu : le titre « Supprimer test_secret, devenu inutile »
sur le texte « D'accord, fais comme tu as dit. » autorise la
suppression de `test_secret`. Le skill `socle-request` dit de ne rien
nommer que l'humain ne nomme ; rien ne l'impose. Ce n'était pas mieux
avant : une question inventée sous `valider` le permettait (B-0185).

## Satisfait quand

- [ ] une décision donnée sans question n'autorise que ce que nomme le texte exact de l'humain
