<!-- socle: couche=backlog zone=publique -->
# B-0337 — Le skill socle-resume tient pour sûr sans mesure ce que porte le message d'un réveil dans la transcription, et où l'humain retrouve ses tâches programmées

> statut : ouvert · origine : J-2026-11-23-R · lu : backlog@b50d4431

Relevé par la passe 1 de la revue de L-0023 (J-2026-11-23-R), constats 3
et 4, sur ce que T-0164 et T-0127 ont écrit dans le skill `socle-resume` :

1. Sans `list_events`, la coupure est « le premier `quotaLimits` qui suit
   le dernier appel du modèle » : rien ne l'ancre avant le réveil. Au tour
   du réveil, les derniers appels sont ceux de ce tour, faits avant la
   lecture ; lue à la lettre, la règle ne trouve aucune coupure, ou prend
   le dernier refus. Et `origin.kind` à `human` n'est mesuré que sur un
   message tapé : rien ne dit si le message d'un réveil (`send_later`) le
   porte aussi, ce qui le compterait parmi les messages de l'humain et
   retiendrait l'agent de reprendre. La branche `list_events` exclut le
   réveil ; celle de la transcription, non. Le cas joue à chaque réveil
   sans `list_events`, celui de chess.
2. Le skill donne claude.ai/code/routines comme la liste des tâches
   programmées où l'humain retrouve ses réveils ; la documentation de
   Claude Code y gère les tâches du compte sans dire si les rappels qu'une
   session se programme y figurent. Le texte part tel quel dans les
   projets installés.

Le skill français n'a qu'environ 130 octets de marge sous son budget de
8 000.

## Satisfait quand

- [ ] sans `list_events`, le réveil lit la coupure du tour d'avant et ne prend pas son propre message pour un message de l'humain, sur une mesure d'un réveil réel
- [ ] l'endroit où l'humain retrouve ses réveils est vérifié, ou dit comme une supposition
