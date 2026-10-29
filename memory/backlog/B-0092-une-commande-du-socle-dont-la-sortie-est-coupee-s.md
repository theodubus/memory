<!-- socle: couche=backlog zone=publique -->
# B-0092 — Une commande du socle dont la sortie est coupée s'arrête avant d'écrire

> statut : ouvert · origine : J-2026-10-29-M · lu : backlog@bc911780

`python3 .socle/socle new backlog "…" | head -1` ne crée aucun sujet : la
commande imprime l'index du backlog avant d'écrire le fichier, `head`
ferme le tube après la première ligne, et la sortie coupée l'arrête en
silence (B-0070 l'a rendue propre, pas complète). Une commande qui écrit
devrait écrire d'abord, ou finir son écriture malgré la sortie coupée.
Sans urgence : on s'en garde en n'y mettant pas de tube.
