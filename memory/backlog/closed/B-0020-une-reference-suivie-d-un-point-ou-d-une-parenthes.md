<!-- socle: couche=backlog zone=publique -->
# B-0020 — Une référence suivie d'un point ou d'une parenthèse est lue avec eux

> statut : fait · origine : J-2026-10-11-D · lu : backlog@c360de10 · ref : J-2026-10-13-E

`memoire.references` lit une référence de commit suivie d'une parenthèse
fermante ou d'un point final avec cette ponctuation, et refuse un SHA
pourtant valide. Deux fois déjà, l'agent a dû
reformuler sa phrase. La fin d'une référence devrait exclure la ponctuation
finale, comme le font les liens Markdown.
