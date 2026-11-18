<!-- socle: couche=backlog zone=publique -->
# T-0003 — Le hook juge l'expression d'un find par la conjonction de ses filtres, et le motif d'un -path sous ses départs

> statut : ouvert · origine : J-2026-11-14-AJ · besoin : B-0231 · lu : backlog@9966bbbd

Un commit : un fichier protégé n'est visé que s'il satisfait chaque filtre d'une même conjonction, et le motif d'un `-path` ne vise que ce qui est sous les départs du `find` ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [ ] `find . -name '*.json' -path './build/*' -delete` passe le hook, `find . -name '*.json' -path './.claude/*' -delete` reste refusé, et un test le montre
- [ ] `find build -path '*.toml' -delete` passe le hook, `find . -path '*.toml' -delete` reste refusé, et un test le montre
