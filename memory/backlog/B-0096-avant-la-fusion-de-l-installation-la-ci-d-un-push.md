<!-- socle: couche=backlog zone=publique -->
# B-0096 — Avant la fusion de l'installation, la CI d'un push refuse un fichier protégé que l'humain corrige

> statut : ouvert · origine : J-2026-10-30-D · lu : backlog@e00eea09

Tant que la branche par défaut n'a pas le socle, la pull request qui
l'installe est tout entière l'installation : la CI de la PR, qui juge
depuis la branche par défaut, n'y voit que des fichiers protégés posés, en
avertissement. Mais la CI d'un push juge depuis le push précédent, où le
socle est déjà posé : un fichier protégé que l'humain corrige avant la
fusion y est refusé faute de validation. Mesuré sur le pilote : Théo a
écrit son nom dans la politique sur la branche de la PR (B-0094 le lui
fait faire), la CI du push est rouge, celle de la PR verte.

Le contrôle des fichiers protégés devrait traiter comme l'installation
toute plage dont la branche par défaut n'a pas encore le socle.
