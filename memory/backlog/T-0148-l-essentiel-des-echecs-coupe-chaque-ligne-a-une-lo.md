<!-- socle: couche=backlog zone=publique -->
# T-0148 — L'essentiel des échecs coupe chaque ligne à une longueur fixe, et n'y fait entrer ni les sorties des tests ni les lignes de code d'une trace

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0296 · lu : backlog@6c894b15

Un commit : `verification.lignes_d_echec` (`engine/socle/verification.py`) coupe chaque ligne à une longueur fixe, et laisse hors de l'essentiel les lignes de code d'une trace (`self.fail(…)`), les sorties `print` des tests et la ligne où un texte imprimé se colle aux points de progression de unittest `-q` (« F.FEconnection error ») ; `essentiel_des_echecs`, dans le hook de l'agent, ne change pas (ADR-0098) ; une note de version. Les valeurs attendues des tests `test_lignes_d_echec_*` de `tests/test_etapes_rapides.py` restent (cherché à la création, D-0141).

## Fait quand

- [ ] une ligne d'échec plus longue que la borne est coupée, et un test le montre
- [ ] sur une sortie de unittest qui a des `print`, un `self.fail(…)` dans une trace et une ligne « F.FEconnection error », l'essentiel ne garde que les tests en échec et le bilan, et un test le montre
