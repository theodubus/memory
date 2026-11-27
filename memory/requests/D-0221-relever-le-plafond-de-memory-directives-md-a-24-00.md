<!-- socle: couche=demandes zone=publique -->
# D-0221 — Relever le plafond de memory/directives.md à 24 000 octets, la clé des garde-fous et le test nommés, comme D-0220

> date : 2026-11-26 · forme : séance

## Question posée

Valides-tu de relever `budgets."memory/directives.md".max_bytes` de 16000 à 24000 dans `.socle/guardrails.toml` et dans les deux gabarits des garde-fous du produit ? Et de changer de 16000 à 24000 la valeur attendue du test `test_l_installeur_pose_les_consignes_vides_et_les_repose_a_la_mise_a_jour`, dans `tests/test_consignes.py` ? C'est le même changement que D-0220, cette fois avec les noms exacts. Réponds `valider` ou `refuser`.
