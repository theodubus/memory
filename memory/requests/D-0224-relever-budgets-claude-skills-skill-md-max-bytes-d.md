<!-- socle: couche=demandes zone=publique -->
# D-0224 — Relever budgets.".claude/skills/*/SKILL.md".max_bytes de 8000 à 10000, ici et dans les deux gabarits des garde-fous, avec la borne de sept tests et l'ensemble PAS_ENCORE vidé, sur D-0223

> date : 2026-11-27 · forme : séance

## Question posée

Une question courte sur le plafond des skills. Le 26 novembre, tu as choisi de le relever de 8 000 à 10 000 octets (D-0223). Ta validation n'autorise le changement que si elle nomme la clé exacte et chaque test, d'où cette question. Valides-tu ces trois changements ?

1. Porter `budgets.".claude/skills/*/SKILL.md".max_bytes` de 8000 à 10000 dans `.socle/guardrails.toml`, `engine/socle/templates/guardrails.toml` et `engine/socle/templates/guardrails.en.toml`.
2. Changer de 8000 à 10000 la borne de taille de ces sept tests :
   - `test_dans_les_deux_langues_ils_passent_leurs_controles`, par sa méthode `texte` (tests/test_skills.py)
   - `test_au_reveil_la_garde_de_la_passation_et_au_premier_tour_la_passation_qui_attend` (tests/test_skills.py)
   - `test_il_est_pose_protege_et_passe_ses_controles_dans_les_deux_langues` (tests/test_skills.py)
   - `test_il_est_pose_protege_sous_son_budget_et_passe_ses_controles` (tests/test_skills.py)
   - `test_il_est_pose_sous_son_budget_et_passe_ses_controles` (tests/test_skills.py)
   - `test_le_skill_socle_batch_colle_le_format_compact_au_recap_de_la_cloture`, dans `tests/test_suite_du_projet.py`
   - `test_le_guide_et_les_skills_disent_ou_va_une_consigne_et_comment_elle_se_leve`, dans `tests/test_consignes.py`
3. Dans `test_chaque_skill_du_produit_laisse_sa_marge_sous_son_plafond` (tests/test_skills.py), vider l'ensemble `PAS_ENCORE`. Il liste les quatre skills dispensés de la marge de 600 octets (socle-batch en français et en anglais, socle-request et socle-resume en français). Ce test-là devient plus strict.

Si tu valides, je fais le changement avec sa note de version, française et anglaise, et son point au prompt de mise à jour de chess. Si tu refuses, le plafond reste à 8 000 et ces quatre skills restent sans marge. Réponds `valider` ou `refuser`.
