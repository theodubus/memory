<!-- socle: couche=backlog zone=publique -->
# B-0328 — La fusion des réglages de Claude Code efface la commande que le projet a mise dans le même bloc qu'un hook du socle

> statut : ouvert · origine : J-2026-11-21-L · lu : backlog@cc3cfb46

Relevé par la revue à froid de L-0008 (J-2026-11-21-L), défaut d'avant
le lot : la fusion des réglages de Claude Code
(`engine/socle/installer.py`, vers les lignes 1575-1576) retire tout bloc
de `hooks` qui contient une commande du socle. Une commande que le
projet a mise dans le même bloc que le hook `Stop` du socle (`bash
tools/lint.sh`, par exemple) disparaît à l'installation et à chaque mise
à jour, sans que l'installeur le dise, et `fins_de_tour_du_projet`
(T-0030) ne la voit plus. Un hook du projet dans son propre bloc est
gardé et nommé. Même défaut pour `SessionStart`.

## Satisfait quand

- [ ] une commande du projet placée dans le même bloc qu'un hook du socle, sous `Stop` comme sous `SessionStart`, survit à l'installation et à la mise à jour, et l'installeur la nomme comme un hook du projet dans son propre bloc
