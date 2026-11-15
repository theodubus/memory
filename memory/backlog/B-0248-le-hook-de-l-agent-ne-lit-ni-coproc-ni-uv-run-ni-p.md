<!-- socle: couche=backlog zone=publique -->
# B-0248 — Le hook de l'agent ne lit ni coproc ni uv run ni poetry run : un push forcé ou la suppression du projet y passent

> statut : ouvert · origine : J-2026-11-15-O · priorité : haute · lu : backlog@b85fce13

La revue du lot B-0234 (J-2026-11-15-O), cinquième constat pour le
backlog : deux voisins hors du lot, par où passent un push forcé ou la
suppression du projet.

- `coproc` n'est pour le hook ni un mot réservé ni un préfixe
  (`RESERVES`, `PREFIXES`, `engine/socle/commands.py`) : `coproc git push
  --force origin main` et `coproc rm -rf ..` passent.
- `uv run` et `poetry run` ne sont pas des préfixes : `uv run rm -rf ..`
  et `uv run git push --force origin main` passent, et `uv run python -c
  …` échappe aux jugements de B-0206 et de B-0228. `uv run` est d'usage
  normal dans un projet uv.

Rien ne rattrape ensuite ni un push forcé ni la suppression du projet :
ADR-0080 (sa première conséquence) ouvre ce sujet, de priorité haute
comme B-0208.

La piste : retirer `coproc` (et le nom de `coproc NOM { …; }`) comme un
mot réservé, et `uv run`, `poetry run` (et leurs options) comme des
préfixes, à la manière de `python -m`.

## Fait quand

- [ ] `coproc rm -rf ..`, `uv run rm -rf ..` et `poetry run git push --force origin main` sont refusés par le hook, `uv run pytest` passe, et un test le montre
