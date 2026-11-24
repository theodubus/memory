<!-- socle: couche=backlog zone=publique -->
# T-0174 — Retirer le lien de la session du prompt de passation : l'option --session, les skills socle-handoff et delegate-lot, la spécification

> statut : ouvert · origine : J-2026-11-24-AF · ref : D-0176 · besoin : B-0345 · lu : backlog@e1d104b0

Un commit : l'option `--session` retirée de `socle handoff prompt`
(`engine/socle/handoff.py`, `engine/socle/cli.py`), ses deux commandes
dans le gabarit de `socle-handoff` et son anglais, la ligne de
`delegate-lot`, le modèle du prompt de la spécification, une note de
version, le prompt de chess ; la copie protégée de `socle-handoff`
remise par une demande. Le test qui affirme le lien :
`test_il_nomme_la_tete_distante_et_l_heure_puis_le_prompt_d_une_session_neuve`
(`tests/test_passation.py`), dont la première ligne attendue passe de
« Passation de https://claude.ai/code/session_x — partante, à
2026-11-24T10:05:00Z. » à « Passation — partante, à
2026-11-24T10:05:00Z. », l'appel sans `session` ; sa question est posée
à Théo le 24 novembre (J-2026-11-24-AF).

## Fait quand

- [ ] `socle handoff prompt` n'a plus d'option `--session`, et son prompt commence par « Passation — <dépôt>, à <heure> », ce qu'un test montre
- [ ] les skills `socle-handoff` et `delegate-lot` et la spécification ne nomment plus le lien, et un test le montre pour le gabarit
