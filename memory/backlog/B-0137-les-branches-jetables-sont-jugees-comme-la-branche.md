<!-- socle: couche=backlog zone=publique -->
# B-0137 — Les branches jetables sont jugées comme la branche de travail : la CI tourne sur chaque push, et un fichier tiers copié y fait juger ses liens morts

> statut : ouvert · origine : J-2026-11-08-S · lu : backlog@e2c6cab9 · après : D-0087

La CI du socle (`socle.yml`) tourne sur tout `push`, branches de prototype
comprises : un `fix:` de prototype la fait échouer. Et `memoire.references`
juge les liens morts d'un fichier tiers copié dans le dépôt, le README d'un
paquet embarqué ; le déclarer dans `[thirdparty] paths` assouplit, donc
demande une validation, même sur une branche qui ne sera jamais fusionnée.
Le pilote a contourné en remplaçant ce README (J-2026-11-08-S).

À cadrer avec Théo : ce qu'est une branche jetable pour le socle, et ce
qu'il y juge encore.

Fait quand :
- [ ] Théo a tranché ce que le socle juge sur une branche jetable, et le socle le fait
