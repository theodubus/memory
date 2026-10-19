<!-- socle: couche=backlog zone=publique -->
# B-0068 — Des chemins tiers, que tous les contrôles du socle ignorent

> statut : en cours · origine : J-2026-10-19-G · lu : backlog@71c25a15

Mesuré à l'essai de cohabitation avec BMAD (F-0022) : les fichiers d'un
outil tiers installé dans le projet (ses skills, ses scripts) sont jugés
comme ceux du projet. Ajouter BMAD est refusé par quatre contrôles, et
chacune de ses mises à jour le serait encore ; l'adoption ne s'en sort
qu'en éteignant trois contrôles pour tout le projet.

À faire : une seule liste de chemins tiers dans les garde-fous, que chaque
contrôle ignore (références, copies, tests, sources du code, mutation,
correspondance code-doc), sans toucher à l'adaptateur. Y ajouter un chemin
assouplit : une décision humaine, que l'installeur peut recueillir quand
il détecte un outil connu (BMAD et ses dossiers) et la proposer à
l'installation. L'adoption n'éteint plus un contrôle pour des fichiers
tiers. Le défaut injecté : un chemin tiers ajouté sans validation.
