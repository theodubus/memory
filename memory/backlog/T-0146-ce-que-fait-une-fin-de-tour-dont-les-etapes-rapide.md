<!-- socle: couche=backlog zone=publique -->
# T-0146 — Ce que fait une fin de tour dont les étapes rapides passent le délai de son hook, soumis à Théo parmi les pistes qui laissent le hook de l'agent tel quel

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0284 · lu : backlog@6c894b15

Un commit : une demande, qui cite B-0284, soumet à Théo l'une des pistes : relever le délai du hook de fin de tour (le gabarit `engine/socle/templates/settings.json`, et la copie protégée de ce dépôt par une demande) ; arrêter avant lui les étapes rapides de la fin de tour, en le disant (`engine/socle/verification.py`) ; ou ranger le cas dans ce que le modèle de menace de B-0258 laisse passer, par une décision. Une piste qui changerait `engine/socle/hooks.py` ne s'ouvre pas : le cas est déduit des réglages, non vu en session (ADR-0098).

## Fait quand

- [ ] une demande soumet la piste à Théo, et sa réponse est consignée au journal
