<!-- socle: couche=backlog zone=publique -->
# B-0229 — Le hook de l'agent ne juge pas le script python qu'un heredoc lui donne (python3 - <<EOF)

> statut : ouvert · origine : J-2026-11-14-AG · lu : backlog@b4ef8718

B-0206 fait juger `python -c` par les chemins protégés que cite son
script, mais pas un script que python lit sur son entrée : `python3 -
<<'EOF'` suivi d'un `open('.socle/policy.toml', 'w')`, ou `python3 <
script.py`. Le corps d'un heredoc n'est que du texte pour le découpage
(`commandes.analyser`) ; le hook laisse donc passer l'écriture d'un
fichier protégé que ce script nomme en toutes lettres. C'est une forme
qu'un agent écrit dans son travail, pour une transformation de plusieurs
lignes : dans le modèle de la règle 2 de D-0112 (ADR-0080), qui la fait
garder. `protege.fichiers` l'attrape ensuite, à la fin du tour et au
commit.

La piste : quand le programme est `python`/`python3` (préfixes retirés),
sans `-c` ni `-m` ni script en argument, et que son entrée est un heredoc,
juger le corps du heredoc comme le script d'un `python -c` (les chemins
protégés cités en toutes lettres) ; un script lu par `<` d'un fichier
reste hors de portée. Ce script se juge aussi par ce qu'il supprime, comme
celui d'un `python -c` dans `hooks.suppressions` depuis B-0228
(`shutil.rmtree('..')`, que rien ne rattrape) : le corps du heredoc passe
par la même lecture (`_supprimes_par_python`).

## Fait quand

- [ ] `python3 - <<'EOF'` dont le corps cite un fichier protégé est refusé par le hook, un heredoc qui n'en cite aucun passe, et un test le montre
