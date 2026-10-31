<!-- socle: couche=backlog zone=publique -->
# B-0105 — Une décision posée dans le widget de questions de l'agent : texte brut, liens morts, sans contexte

> statut : fait · origine : J-2026-10-31-C · lu : backlog@76346369 · ref : J-2026-10-31-C

L'agent du pilote posait ses décisions à Théo dans le widget de questions
de Claude Code : un bloc de texte brut, des liens qui ne se suivent pas,
des options écrites par l'agent. Théo ne pouvait ni valider ni refuser en
sachant de quoi il parlait. Rien dans le socle ne l'écartait, et ses
instructions donnaient l'approbation d'une spécification pour exemple
d'une décision en séance.

Fait (ADR-0038) : le hook de l'agent refuse le widget, et le gabarit du
réglage de Claude Code le lui montre ; une décision qui demande du
contexte s'écrit en demande, dont le lien se donne dans la conversation.
Un défaut injecté (`question-en-widget`) et un test l'éprouvent.
