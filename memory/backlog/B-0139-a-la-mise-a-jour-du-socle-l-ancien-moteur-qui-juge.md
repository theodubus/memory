<!-- socle: couche=backlog zone=publique -->
# B-0139 — À la mise à jour du socle, l'ancien moteur qui juge la CI compte les clés nouvelles des garde-fous pour un assouplissement

> statut : ouvert · origine : J-2026-11-08-S · lu : backlog@9dbc0778

La mise à jour du socle nomme les réglages nouveaux du gabarit des
garde-fous, à déclarer une fois le moteur nouveau commité, parce que
l'ancien moteur, qui juge encore la CI, compte une clé inconnue pour un
assouplissement (B-0123). Le pilote a vu sa CI rester rouge jusqu'à la
validation des fichiers protégés (J-2026-11-08-S). Chercher un ordre, ou un
jugement par le moteur nouveau, qui laisse la CI verte.

Fait quand :
- [ ] une mise à jour qui apporte des clés nouvelles aux garde-fous laisse la CI verte, prouvé sur un projet d'essai
