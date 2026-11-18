<!-- socle: couche=backlog zone=publique -->
# T-0050 — Les textes du produit qui disent encore « sujet » d'une entrée du backlog et que des tests lisent mot pour mot

> statut : ouvert · origine : J-2026-11-16-U · besoin : B-0265 · après : D-0132 · lu : backlog@9966bbbd

T-0046 a changé le format, le guide, les skills, les instructions posées,
l'état et les messages des contrôles. Il a laissé ce qui dit encore
« sujet » d'une entrée du backlog et que des tests lisent mot pour mot,
dont le changement attend une demande validée qui nomme ces tests :

- le dossier de la revue (`engine/socle/review.py` : « Les sujets du lot :
  leur critère « Fait quand » est ta barre », la consigne du relecteur)
  et la phrase du skill `socle-review` qui le décrit (« puis celles que
  ses sujets citent ») ;
- les questions de départ (« une pull request par sujet »,
  `engine/socle/initialization.py`) et le gabarit des questions de
  cadrage (`engine/socle/templates/questions.md`) ;
- la règle du hook dans le guide (« Un trou ouvre un sujet »), les mots
  que Théo a validés (D-0120) : les changer est à lui demander.

## Fait quand

- [ ] le dossier de la revue, son skill, les questions de départ et de cadrage disent tâche, besoin ou entrée du backlog, jamais « sujet », dans les deux langues, et leurs tests le lisent ainsi
