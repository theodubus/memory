<!-- socle: couche=backlog zone=publique -->
# B-0350 — L'étape 3 du skill socle-batch fait attendre la CI sur la ligne « CI » de l'état, qui suit la tête locale : un commit fait pendant l'attente la déplace, et l'agent attend le mauvais commit

> statut : fait · origine : J-2026-11-24-AV · ref : J-2026-11-24-AX, T-0176, D-0181, J-2026-11-24-AU, J-2026-11-24-AS · lu : backlog@a59a30df

Relevé par la revue de cap 5 (J-2026-11-24-AU), retenu par Théo
(D-0181). L'étape 3 du gabarit de `socle-batch`
(`engine/socle/templates/skills/socle-batch/SKILL.md` et son anglais)
fait attendre `success` sur le SHA court du commit de tête, dans la
ligne « CI » de `socle state`. Cette ligne lit, depuis T-0161, les
exécutions du commit de tête local : un commit fait pendant l'attente la
déplace, et elle dit « aucune exécution » sur un commit que la CI n'a
pas reçu, pendant que celle du commit poussé a fini. Vu trois fois en
usage réel (J-2026-11-13-B, J-2026-11-24-AR, J-2026-11-24-AS : #91
fusionnée en retard). L'atelier l'a corrigé dans son seul skill
`delegate-lot` (ab70b8bc) : l'attente suit les exécutions du commit
poussé, par son SHA (`gh run list --commit <sha>`).

## Satisfait quand

- [x] l'agent d'un projet installé attend la CI du commit qu'il a poussé, même quand un commit local s'ajoute pendant l'attente
