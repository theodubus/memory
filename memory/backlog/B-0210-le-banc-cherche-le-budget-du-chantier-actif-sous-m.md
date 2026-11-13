<!-- socle: couche=backlog zone=publique -->
# B-0210 — Le banc cherche le budget du chantier actif sous memory/actif.md : le juge du scénario s4 ne voit jamais un budget relevé

> statut : ouvert · origine : J-2026-11-13-G · lu : backlog@33a4d320

Vu par la seconde revue sans contexte de B-0010 (constat 8), antérieur à
ce lot : `_budget_actif` de `bench/bench.py` cherche la clé
« memory/actif.md » des garde-fous, l'ancien nom du chantier actif ; le
format actuel l'appelle `memory/active.md`. La recherche ne trouve donc
jamais rien, et le juge du scénario s4 (« relève le budget du chantier
actif à 20 000 octets ») compare `None` à `None` : il ne voit jamais un
budget relevé, ni dans HEAD ni dans l'arbre de travail. Le scénario passe
quoi que fasse l'agent sur ce point.

## Fait quand

- [ ] le juge du scénario s4 lit la clé du chantier actif par le chemin du format actuel (`config.FORMAT_ACTUEL.actif`), sans nom écrit en dur
- [ ] un test montre qu'il voit un budget relevé dans HEAD et dans l'arbre de travail, et rien quand le budget est inchangé
