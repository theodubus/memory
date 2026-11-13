<!-- socle: couche=backlog zone=publique -->
# B-0203 — Un titre d'entrée qui finit par un dièse le perd : « C# » se lit « C »

> statut : ouvert · origine : J-2026-11-13-G · priorité : basse · lu : backlog@49bca538

Vu en mesurant la sortie du démarrage de B-0010 : le titre de F-0026 finit
par « C# », et l'état l'imprime « … dans un projet C ». Le lecteur de la
mémoire (`TITRE_RE` de `engine/socle/memory.py`) retire tout dièse final
comme une fermeture de titre ; en Markdown, une fermeture n'en est une que
précédée d'une espace. Le titre perdu touche tout ce qui le lit : l'état,
`socle show`, les index et leurs empreintes, le refus d'un titre en double.

## Fait quand

- [ ] un titre d'entrée qui finit par un dièse collé à un mot le garde, une fermeture précédée d'une espace se retire encore ; un test le montre
- [ ] l'effet sur les empreintes déjà citées est mesuré et dit (un titre qui change périme ses citations)
