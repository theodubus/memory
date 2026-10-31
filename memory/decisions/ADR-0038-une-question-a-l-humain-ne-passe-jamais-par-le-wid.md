<!-- socle: couche=decisions zone=publique -->
# ADR-0038 — Une question à l'humain ne passe jamais par le widget de l'agent ; une décision qui demande du contexte s'écrit en demande

> statut : acceptée · date : 2026-10-31 · source : J-2026-10-31-C@14332162 · lu : decisions@a5a9abfc

## Contexte

L'humain répond dans la conversation, et l'agent consigne sa réponse mot
pour mot (ADR-0006@3841810a). Une décision en séance en est la forme
courte, née pour les approbations dans la conversation que demandaient
les workflows de BMAD, retiré depuis (ADR-0036@d5c2b493). Sur le pilote,
l'agent a posé l'approbation de la spécification dans le widget de
questions de Claude Code : un texte brut, des liens qui ne se suivent
pas, des options qu'il avait écrites. Théo ne pouvait ni valider ni
refuser en sachant de quoi il parlait, et a demandé une demande, avec son
lien dans la conversation (J-2026-10-31-C@14332162).

## Décision

- **Le hook de l'agent refuse le widget de questions** (sous Claude Code,
  l'outil `AskUserQuestion`), avec le remède : la demande, ou une question
  courte dans le texte de la réponse. Le gabarit du réglage de Claude Code
  ajoute l'outil à ce que le hook voit.
- **Une décision qui demande du contexte**, approuver un document compris,
  s'écrit en demande, dont le lien se donne dans la conversation.
- **La séance** reste à ce que l'humain tranche dans la conversation, de
  lui-même ou sur une question courte posée dans le texte de la réponse.

## Conséquences

L'humain lit chaque décision dans un document qui se suffit, avec des
liens qu'il suit, et y répond avec ses mots. Le prix : une approbation
coûte une demande entière ; le widget n'est plus disponible, même pour
un choix simple, qui se pose en texte. Un projet installé le reçoit à la
mise à jour de son socle, dont l'humain approuve le réglage changé. Pour
défaire : retirer l'outil du matcher et le refus du hook.
