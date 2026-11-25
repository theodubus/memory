<!-- socle: couche=demandes zone=publique -->
# D-0184 — Le changement du test de T-0174 : la première ligne attendue du prompt de passation, sans le lien de la session qui part

> date : 2026-11-24 · forme : séance

## Question posée

Valides-tu le changement d'un test de T-0174 ? T-0174 retire du prompt de passation le lien de la session qui part (D-0176). Le test `test_il_nomme_la_tete_distante_et_l_heure_puis_le_prompt_d_une_session_neuve` (`tests/test_passation.py`) voit sa première ligne attendue passer de « Passation de https://claude.ai/code/session_x — partante, à 2026-11-24T10:05:00Z. » à « Passation — partante, à 2026-11-24T10:05:00Z. », l'appel sans `session`.
