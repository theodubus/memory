<!-- socle: couche=backlog zone=publique -->
# T-0201 — Pendant une mise à jour pas encore commitée, les hooks avant commit et avant push ne refusent que les constats que le commit ou le push apporte

> statut : ouvert · origine : J-2026-11-26-AA · besoin : B-0357 · après : T-0200 · lu : backlog@35e9325c

La conception de B-0357, son ADR d'abord : dans un projet installé (mode
projet) dont la copie du moteur, dans l'arbre de travail, diffère de
celle du dernier commit, `git_pre_commit` juge l'index et le dernier
commit avec le moteur neuf, et ne refuse que les constats de l'index
absents du dernier commit ; `git_pre_push` de même entre le commit poussé
et la base. Le refus dit, d'une ligne, qu'une mise à jour est en cours et
que les constats déjà commités sont laissés à la CI. En mode amont, et
hors d'une mise à jour, rien ne change.

## Fait quand

- [ ] un test pose un projet installé, remplace sa copie du moteur dans l'arbre par une copie qui refuse un fichier déjà commité, et vérifie que le hook avant commit accepte un commit qui n'ajoute qu'une demande, puis refuse un commit qui ajoute un fichier refusé
- [ ] un test vérifie de même que le hook avant push accepte le commit de la demande seule
- [ ] un test vérifie qu'en mode amont le hook avant commit refuse encore un constat déjà commité
