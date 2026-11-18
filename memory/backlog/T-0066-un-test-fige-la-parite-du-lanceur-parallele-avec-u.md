<!-- socle: couche=backlog zone=publique -->
# T-0066 — Un test fige la parité du lanceur parallèle avec unittest discover, et son bilan lit le résumé de chaque module sur un flux à part

> statut : ouvert · après : D-0130 · origine : J-2026-11-17-J · besoin : B-0281 · lu : backlog@7ce97339

Un test compare `parallele.modules(RACINE)` aux modules que
`unittest.TestLoader().discover("tests", top_level_dir=".")` charge. Le
lanceur garde la sortie standard et la sortie d'erreur de chaque module à
part, et lit le résumé de `unittest` (« Ran N tests », « OK »,
« FAILED ») sur la sortie d'erreur seule.

## Fait quand

- [ ] un test échoue si un fichier de tests n'est lancé que par l'un des deux
- [ ] un test montre qu'un module dont un test imprime « Ran 99 tests », sortie standard tamponnée, ne compte que ses propres tests
