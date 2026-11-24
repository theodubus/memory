# Passation de L-0010

Le 24 novembre 2026, la fenêtre de cinq heures à 91 %, la session qui
menait L-0010 a rangé ici ses sept commits que la revue du lot n'avait
pas encore vus, en correctifs (`git format-patch`), la branche de travail
`ccr-1ce8bc05-qb7vdl` revenant à `7204705`, poussé.

## Ce qu'ils contiennent

1. La réponse `valider` de Théo à D-0174 (« Valider D0174 »), T-0039,
   T-0041 et T-0080 closes. Elle autorise le changement des deux valeurs
   attendues que D-0174 nomme : elle doit partir dans le même push qu'eux
   (correctif 3).
2. T-0081 : la commande `socle handoff` (`prompt`, `check`), sa garde,
   ses défauts injectés et son témoin sain, la reprise de `socle-resume`.
3. T-0079 : le skill `socle-handoff`, « Changer de session » de
   `socle-batch` réduit, les instructions, le guide, les deux tests de
   D-0174, la note de version 2026-11-24-c.
4. T-0134 et T-0162 : deux règles du skill des lots et du format, la
   note 2026-11-24-d ; B-0303, B-0335, B-0259 et B-0156 satisfaits ;
   `delegate-lot` donne le prompt de `socle handoff prompt`.
5. Le prompt de mise à jour de chess, points 72 et 73.
6. La passe 3 de revue écrite dans L-0010 : son relecteur a été arrêté
   avant d'avoir rendu.
7. L'entrée du journal de cette passation.

`python3 .socle/socle verify --fast` passait sur le commit 5.

## Reprendre

1. Sur la branche de la session neuve, partie de `main` :
   `git merge --no-edit origin/ccr-1ce8bc05-qb7vdl`, puis
   `git am docs/fabrication/passation-l-0010/*.patch`, puis retirer ce
   dossier et la ligne 0 des « Prochaines étapes » du chantier actif,
   qui y renvoie, dans un commit.
2. La revue du lot sur la plage appliquée (`python3 .socle/socle review
   --batch L-0010 --base <le commit d'avant le premier correctif>`), avec
   les points à éprouver de la passe 3 : la garde contre la
   spécification validée, `socle handoff prompt`, la reprise de
   `socle-resume`, le skill contre la spécification, les deux valeurs
   attendues seules changées, les défauts injectés, B-0259 et B-0156
   fermés. Ses bloquants corrigés.
3. La demande qui remet les copies protégées de `socle-batch`,
   `socle-resume` et `socle-handoff` (`.claude/skills/`), chacune à
   l'empreinte de son gabarit français (les 16 premiers caractères de son
   `sha256`), puis, validée, l'installeur relancé en mode amont ; sa
   réécriture de la section du socle d'`AGENTS.md` se défait si elle
   passe le budget, comme le 24 novembre (J-2026-11-24-N).
4. La clôture de L-0010, le push, la pull request, sa fusion une fois la
   CI verte, la distribution vérifiée.
