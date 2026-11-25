# Passation de L-0036

Le 24 novembre 2026, la fenêtre de cinq heures à 76 %, la session qui
menait L-0036 a rangé ici ses onze commits que la revue du lot n'a pas
encore vus, en correctifs (`git format-patch`), la branche de travail
`ccr-4b9c6962-fq3m9y` revenant à `cd6c6827`, poussé. Les identifiants
nouveaux qu'ils créent ne se citent qu'une fois appliqués.

## Ce qu'ils contiennent

1. T-0175 : une entrée du journal ne note aucun geste futur pour
   l'humain (`FORMAT.md`, les gabarits d'`AGENTS.md`), note 2026-11-24-j.
2. T-0176 : le gabarit de `socle-batch` attend la CI du commit poussé,
   note 2026-11-24-k.
3. T-0178 : un `Corrige:` hors du dernier paragraphe fait un correctif
   (`est_correctif`), son ADR et son modèle de menace, le défaut injecté
   et son témoin sain, note 2026-11-24-o.
4. T-0179 sort du lot pour un lot à part.
5. Le prompt de mise à jour de chess, points 79 à 81.
6. T-0177 : l'état ne liste plus « à réécrire » une demande renvoyée
   qu'une autre cite ; la règle dans `FORMAT.md` et le gabarit de
   `socle-request`, note 2026-11-24-n.
7. T-0174 : `socle handoff prompt` sans `--session`, le gabarit de
   `socle-handoff`, la spécification, note 2026-11-24-m, points 82 et 83
   du prompt de chess ; la décision de séance de Théo qui autorise la
   seule valeur attendue changée : elle part dans le même push qu'elle.
8. Trois décisions de Théo (la revue de cap hors du produit pour
   l'instant, B-0346 avant chess, l'abandon des deux suggestions gardées),
   la tâche et le lot de B-0346.
9. L'entrée du journal de cette passation.
10. La réponse de Théo sur la passation : le prompt à copier, le
    commutateur de l'atelier restant manuel pour l'instant.
11. La réponse de Théo « oui après chess » : un besoin pour que l'agent
    supprime lui-même ses branches de travail déjà contenues ailleurs.

Les tests ciblés de chaque tâche passaient ; la dernière vérification
rapide entière, au commit 2, passait.

## Reprendre

1. Sur la branche de la session neuve :
   `git merge --no-edit origin/ccr-4b9c6962-fq3m9y`, puis
   `git am docs/fabrication/passation-l-0036/*.patch`, puis retirer ce
   dossier dans un commit.
2. La revue du lot sur la plage appliquée (`python3 .socle/socle review
   --batch L-0036 --base cd6c6827`), skill `socle-review` : la seule
   valeur attendue changée, le défaut injecté de T-0178 et le faux
   positif d'une ligne de prose qui commence par `Corrige:`, les deux
   gabarits de `socle-batch` sous leur budget de 8 000 octets.
3. La demande qui remet les copies protégées de `socle-batch`,
   `socle-handoff` et `socle-request`, les empreintes des gabarits après
   la revue, relue à froid, puis l'installeur en mode amont sur sa
   réponse.
4. La clôture de L-0036, le push, la pull request, sa fusion par
   l'agent, la distribution.
