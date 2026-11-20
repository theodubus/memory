<!-- socle: couche=backlog zone=publique -->
# B-0320 — Pousser sous un autre nom de branche la réécriture de ce qu'une branche a poussé la juge comme neuve : le hook avant push ne voit pas la valeur attendue affaiblie

> statut : ouvert · origine : J-2026-11-20-AQ · lu : backlog@a5356c77

ADR-0104 juge la plage d'une branche distante disparue sans fusion
depuis le dernier commit que ce clone y a poussé, gardé par référence
distante. Une référence neuve, sans trace, se juge toujours contre la
branche par défaut : la valeur attendue d'un test que seule la branche
`x` a ajouté, poussée, puis affaiblie et poussée sous `x-2`, passe le
hook avant push, et la CI de la pull request de `x-2`, qui juge contre la
branche par défaut, aussi. Contrairement à la suppression de la branche
distante, l'agent le peut seul, sans l'humain. Son modèle de menace le
laisse hors de la décision.

Pistes : juger une référence neuve aussi depuis les commits gardés des
autres références que son commit local réécrit (même fichier de test,
même entrée), sans fusion ; ou dire, dans une décision, pourquoi ce
contournement exprès reste hors du modèle d'un agent coopératif.

## Satisfait quand

- [ ] la réécriture, poussée sous un nom neuf, de ce qu'une autre branche de ce clone a poussé sans fusion est refusée par le hook avant push comme elle l'aurait été sur cette branche, ou une décision accepte ce risque et le dit
