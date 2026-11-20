<!-- socle: couche=backlog zone=publique -->
# B-0308 — Le hook de l'agent ne juge pas le script qu'un heredoc écrit dans un fichier puis que python lance dans la même commande

> statut : abandonné · origine : commit:3e83907e · ref : D-0143 · lu : backlog@bbae2a79

Relevé par la passe 1 de la revue de L-0019, sur le commit relu, mesuré
avant et après le lot : une commande qui écrit un script par un heredoc
(`cat > /tmp/x.py <<'EOF'`) puis le lance (`python3 /tmp/x.py`) passe le
hook, que le corps fasse `shutil.rmtree('..')` ou écrive le réglage
local de Claude Code, que git ne suit pas, pour couper les hooks. T-0001
(ADR-0094) juge le corps d'un heredoc que python lit sur son entrée,
pas celui qu'un autre programme écrit dans un fichier ; B-0229 l'avait
exclu de son périmètre. Un agent écrit cette forme, et rien ne rattrape
son effet. La conception n'est pas tranchée : suivre le fichier écrit
jusqu'au `python` qui le lance dans la même commande, ou juger tout
corps de heredoc écrit dans un fichier `.py`.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Satisfait quand

- [ ] un script de python écrit par un heredoc puis lancé dans la même commande se juge comme le script d'un `python -c`
