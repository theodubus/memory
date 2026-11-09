<!-- socle: couche=demandes zone=publique -->
# D-0084 — Revalider, dans le push des tests, les deux valeurs attendues que D-0083 a validées

> date : 2026-11-09 · forme : séance

## Question posée

Revalidez-vous les deux valeurs attendues déjà validées par D-0083 ? Ce sont les tests `test_les_adaptateurs_maintenus` et `test_un_projet_par_adaptateur_nouveau`, qui comptent désormais `kotlin` parmi les adaptateurs maintenus. Le hook refuse le push parce que la validation de D-0083 est partie dans un push antérieur.
- Si vous répondez « valider », votre réponse part dans le même push que les tests, et les trois commits locaux rejoignent la PR #25.
- Sans votre réponse, ils restent dans le seul conteneur.
