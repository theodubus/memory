<!-- socle: couche=backlog zone=publique -->
# B-0302 — Un test du hook ne range jamais un trou connu parmi les témoins qui doivent passer : une liste de limites connues, chacune avec l'entrée du backlog qui la bouchera, et le relecteur vérifie chaque témoin nouveau (D-0141)

> statut : ouvert · origine : J-2026-11-19-AJ · ref : D-0141, D-0140, B-0230 · lu : backlog@cb1c44d7

Théo a retenu le 19 novembre la proposition 1 (D-0141, J-2026-11-19-AJ).
Un test du hook a deux listes : les commandes qui doivent être refusées,
et celles qui doivent passer, les témoins sains. Le 14 novembre, `find .
-type f | xargs sed -i s/a/b/` est entré dans la seconde liste de
`test_cp_t_find_xargs_bash_ec_sort_o_et_python_c` (`tests/test_garde.py`)
alors qu'elle réécrit les fichiers protégés : le hook ne la voyait pas.
Le test figeait un trou comme correct ; quand T-0002 le bouche, il faut
une demande (D-0140), comme pour un test affaibli.

La règle retenue : un témoin qui doit passer est réellement sans danger
(il n'écrit aucun fichier protégé, ou un filtre les écarte, et ne
supprime rien du projet) ; un trou connu ne s'écrit jamais dans cette
liste, mais dans une liste de limites connues, chacune avec l'entrée du
backlog qui la bouchera ; le relecteur de chaque lot vérifie que chaque
témoin sain nouveau l'est. La politique ne change pas : déplacer une
limite vers les refus reste un changement de valeur attendue, soumis à
une demande.

## Satisfait quand

- [ ] les listes des commandes qui doivent passer, dans les tests du hook, ne contiennent que des commandes sans danger, chaque trou connu figé étant dans une liste de limites qui cite son entrée du backlog ouverte
- [ ] la consigne du relecteur dit de vérifier que chaque témoin sain qu'un lot ajoute l'est réellement
