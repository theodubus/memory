<!-- socle: couche=backlog zone=publique -->
# B-0341 — L'auto-test échoue par intermittence en CI : un cas clone l'origine partagée, liée en dur, pendant qu'un autre y pousse

> statut : ouvert · origine : J-2026-11-24-A · priorité : haute · lu : backlog@4a658caa

Vu dans la CI de chess le 23 novembre, sur le socle publié le 12 (le
texte exact de la session chess est dans J-2026-11-24-A) : le job de
l'auto-test échoue sur `RuntimeError: git clone -q …/origine …/cas-200 :
fatal: hardlink different from source at '…/objects/tmp_objdir-incoming-…'`,
levée par `a.clone()` dans `jouer()`, sous le `ThreadPoolExecutor` de
`selftest.executer` ; le même commit est vert dans l'autre exécution du
jour. L'hypothèse : les cas joués en parallèle clonent la même origine
par un clone local, qui fait des liens durs, pendant qu'un autre y
pousse, et la quarantaine du push change sous le clone. Et le clone est
hors du `try` : un clone qui échoue fait tomber tout l'auto-test au lieu
d'un cas. À la publication du 23 novembre, rien ne semble l'avoir
changé : à établir.

## Satisfait quand

- [ ] l'auto-test n'échoue plus par intermittence sur un clone de l'origine partagée, et un clone qui échoue n'échoue que son cas
