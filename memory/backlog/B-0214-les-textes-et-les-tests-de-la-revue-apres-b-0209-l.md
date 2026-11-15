<!-- socle: couche=backlog zone=publique -->
# B-0214 — Les textes et les tests de la revue après B-0209 : le dossier décrit à moitié, le modèle de menace d'une décision, une fonction sans emploi, deux cas sans test, l'AGENTS.md de ce dépôt en retard

> statut : ouvert · origine : J-2026-11-14-A · priorité : basse · lu : backlog@213ad9b5

La revue de B-0209 (J-2026-11-14-A), constats 5 à 9, des restes de texte
et de test.

- Le gabarit du skill `socle-review` (français et anglais) ne dit pas que
  le dossier donne les décisions que le lot écrit ;
  `docs/fabrication/architecture.md` décrit encore « les sujets qu'il
  ferme ».
- ADR-0073 permet d'écrire le modèle de menace dans la décision que le
  sujet cite ; FORMAT.md, le gabarit d'AGENTS.md et le skill ne parlent
  que de la section du sujet.
- `sujets_fermes` de `engine/socle/review.py` ne sert plus que les
  tests ; un test de `tests/test_revue.py` vérifie l'absence d'un titre
  qui n'existe plus (le retirer demande une demande validée).
- Sans test : un sujet clos et rangé dans `closed/` par le lot ; un sujet
  privé.
- La section du socle de l'AGENTS.md de ce dépôt est en retard sur son
  gabarit (la règle de B-0209, la phrase des branches jetables) : à 2
  octets de son budget de 16 000, elle ne peut les recevoir sans qu'on y
  fasse de la place.

La revue de B-0212 (J-2026-11-14-H), constat 7 : trois des tests de
`TestLotDejaPousse` (`tests/test_revue.py`) échouent sur le commit
parent par `AttributeError`, avant leur assertion de comportement ; le
défaut qu'ils visent (les sujets de `--since` perdus quand tout est
poussé) est réel, mais aucun test ne le prouve sur le parent.

Le 15 novembre, Théo valide D-0116 (J-2026-11-15-H) : la consigne du
relecteur suit la règle 1 de D-0112, et `sujets_fermes` se retire, les
trois tests que D-0116 nomme changeant comme elle le dit ; sa réponse se
consigne dans le push de ce changement. L'attente sur le titre disparu
reste (D-0116 ne la retire plus). Le même jour, D-0117 : le relecteur
reçoit, explicitement, le modèle le plus capable disponible jusqu'à
Opus, jamais un moindre que celui qui a implémenté ; Fable seulement si
l'humain le demande ; découplé du modèle de la session, que la règle du
modèle de `socle-batch` peut faire moins coûteux.

## Fait quand

- [ ] les textes de la revue disent ce que donne le dossier et où s'écrit le modèle de menace, d'une seule manière
- [ ] les deux cas ont leur test, et `sujets_fermes` est retiré ou sert
- [ ] la section du socle de l'AGENTS.md de ce dépôt suit son gabarit, sous son budget
- [ ] le skill de revue du produit, en français et en anglais, donne au relecteur le modèle de D-0117, explicitement à son lancement, et un test le montre
- [ ] la consigne du relecteur et les trois tests de D-0116 suivent D-0116, sa réponse consignée dans le même push
