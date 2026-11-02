<!-- socle: couche=backlog zone=publique -->
# B-0123 — Une mise à jour ne signale pas les réglages nouveaux des garde-fous à un projet existant

> statut : ouvert · origine : J-2026-11-01-N · lu : backlog@74166902

Relevé en préparant la relecture de la documentation (B-0121). À une
mise à jour, l'installeur garde le fichier des garde-fous du projet tel
quel (« conservé, comparer au gabarit à la main ») : les réglages nouveaux
du gabarit, comme `[specs] paths` et `[tests] case_paths` (B-0120), n'y
arrivent pas, et l'agent du projet ne sait pas qu'il peut les déclarer.

À faire : l'étape de mise à jour nomme les réglages du gabarit absents du
projet, avec ce qu'ils font ; les déclarer durcit, l'agent le fait seul.
D'ici là, le message de mise à jour du pilote le lui dit.
