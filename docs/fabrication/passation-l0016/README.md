# Passation du lot L-0016

Quatre commits ont été faits le 18 novembre dans la session ouverte à 17 h 24 UTC. Le dernier correctif de code n'est pas encore relu. Après la correction des bloquants de la passe 1, la fenêtre de cinq heures a atteint 67 %. C'est au-delà du seuil de 60 % où le skill `socle-batch` ne lance plus de sous-agent, et la passe 2 de la revue en demande un.

Les commits partent de 52e3489, la tête de la branche avant ce dossier. Ils s'appliquent d'un trait par `git am`, sur 52e3489, avec la date de l'auteur pour date du commit et le même auteur du commit (Claude, noreply@anthropic.com). Ils redonnent alors les mêmes SHA. Vérifié dans un clone : la tête obtenue est c034332, l'arbre est celui de la session. Les SHA que citent leurs entrées de journal et la section « Revues » de L-0016 restent donc justes.

Ce dossier se retire au commit qui les intègre. Les identifiants qu'ils créent ne se citent ici que par leur numéro, ou par leur date et leur lettre : la base ne les a pas.

## Ce qu'ils portent

1. **0001 (381025a)** : T-0088. Le rendu de `socle roadmap` suit les deux exemples que Théo a validés (D-0127) : le compact aligné en colonnes, le détaillé en un tableau par lot. Le commit apporte aussi dix tests nouveaux, le guide et son anglais, la note 2026-11-18-c, le point 17 du prompt de chess et l'entrée de journal du 18 novembre, lettre O. T-0088 reste ouverte jusqu'à la réponse de Théo.
2. **0002 (427db82)** : la passe 1 de la revue (journal, lettre P), écrite dans L-0016. Elle trouve deux bloquants. Les tâches 89 et 90 vont au backlog, et B-0285 est complété.
3. **0003 (5e5837d)** : la correction des deux bloquants (journal, lettre Q).
   - La décision 89 : le hook de fin de tour ne cherche plus les deux lignes du récap dans un bloc de code délimité. Elle a son modèle de menace, un défaut injecté et son témoin.
   - La suite suit l'ordre d'exécution : l'en-tête d'un jalon se répète quand il revient, et une fenêtre commune à tous les jalons montre le lot en cours et les deux suivants.
4. **0004 (c034332)** : la doc d'architecture, et le recul de la passe 1, « continuer » (journal, lettre R). Au backlog : la tâche 91 dans L-0006, le besoin 287 et sa tâche 92.

`tests-existants.diff` contient les dix tests, qui existaient avant le lot, dont la valeur attendue change. Ils sont tous dans `tests/test_suite_du_projet.py` :
- `test_le_format_compact_une_ligne_par_jalon_et_par_lot_le_lot_en_cours_marque`
- `test_le_format_compact_par_besoin`
- `test_le_format_detaille_par_lot`
- `test_le_format_detaille_suit_le_lot_en_cours_et_les_deux_suivants_all_les_suit_tous`
- `test_le_format_detaille_par_besoin_chaque_tache_avec_son_lot`
- `test_le_format_detaille_donne_le_lien_de_chaque_demande_et_de_ce_qui_revient_a_l_humain`
- `test_en_anglais`
- `test_socle_roadmap_et_ses_options`
- `test_by_prend_batch_ou_need_et_batch_par_defaut_sans_synonyme`
- `test_la_ci_posee_ecrit_le_format_detaille_dans_le_resume_de_son_execution`

Ce diff s'applique après la série et reste dans l'arbre, hors de tout commit, jusqu'à la réponse de Théo. Sans elle, `tests.attendus` le refuse, et sans lui `verify.tests` échoue. Quand le hook de fin de tour bloque là-dessus, le dire en une ligne.

`demande-brouillon.txt` : la demande à Théo, prête sauf trois points : le résultat des revues, les empreintes à prendre, les liens à prendre après le push.

## Reçu de Théo après la passation

Théo a reçu deux fois de suite, dans « Pour toi », la demande de supprimer `ccr-b742f301-i57kk1` et `ccr-d82b39da-2j0guo`. Ces deux branches n'existaient plus sur GitHub : l'état les lisait dans les références locales du dernier fetch, que rien n'élague (B-0193, T-0024). Son message, mot pour mot : « Pourquoi tu continues de me demander de supprimer des branches que j'ai deja supprimé et que tu ne prends que l'info quand je te le dis alors que tu as accès à la liste des branches existantes sir github ».

Ce qui a été fait :
- un `git fetch --prune origin` a effacé les deux références ;
- B-0193 passe en priorité haute, avec cette citation ;
- T-0024 sort de L-0007 pour un lot à elle, L-0017, après L-0016 et avant L-0015 ;
- le chantier actif dit de vérifier sur GitHub une branche avant de la donner à supprimer.

L'entrée de journal qui consigne ce message, avec son texte exact, s'écrit après l'intégration des correctifs : écrite avant, elle aurait pris la lettre qu'ils portent déjà.

Puis, sur le coût du lot, mot pour mot : « L0016 était un correctif de format de roadmap, je comprends pas pourquoi il a consommé 75% d'une session / Et la tel que c'est parti j'ai l'impression que L0017 va être pareil alors qu'en soit c'est juste le fait de check les branches github avant de demander de supprimer / Est ce que c'est juste un constat ponctuel ou est ce qu'il y a une lourdeur non nécessaire superflue avec le fonctionnement du socle ? »

La fenêtre de cinq heures, mesurée pendant la session, de 1 % à 75 % :
- l'implémentation : environ 30 points (328 000 jetons) ;
- la passe 1 et la correction de ses bloquants : environ 31 points (216 000 et 247 000 jetons) ;
- l'orchestration : environ 5 points ;
- la passation et la réponse sur les branches : environ 8 points.

La réponse de l'agent, dans la conversation, distingue ce qui tient à ce lot de ce qui tient au fonctionnement du socle, et propose des allégements. L'entrée de journal qui consigne la question et la réponse de Théo, et le besoin qui en sort, s'écrivent après l'intégration, pour la même raison que plus haut : avant, ils prendraient les numéros que portent déjà les correctifs.

Théo a ensuite validé les cinq propositions, la 2 dans sa variante légère, la 1 sous la condition que les sous-agents d'implémentation restent pertinents, que la réponse de l'agent remplit : D-0134, en séance, qui désigne `docs/fabrication/allegements.md`, où sont les propositions, sa réponse et celle de l'agent. Après l'intégration, ouvrir au backlog :
- un besoin par proposition, avec ses tâches ;
- un lot des allégements, après L-0017 et avant L-0015 ;
- pour la 2, la tâche qui la porte dans le skill `socle-request` du produit. Le skill `delegate-lot` la dit déjà.

La variante légère vaut dès maintenant : les dix tests de `tests-existants.diff` se valident par une question dans la conversation qui les nomme, chacun avec sa valeur avant et après. La réponse se consigne en séance, sans demande écrite ni relecture à froid. Elle se commite avec les tests, dans le même push.

## La suite

1. **Intégrer en gardant les SHA.** Copier ce dossier hors du dépôt (dans le scratchpad de la session), puis :
   - `git checkout --detach 52e3489`
   - `git -c user.name=Claude -c user.email=noreply@anthropic.com am --committer-date-is-author-date <copie>/000*.patch`, qui donne la tête c034332 ;
   - `git merge --no-edit claude/socle-roadmap-l-0016-drf6h3`, qui reprend ce dossier et le chantier actif ;
   - retirer ce dossier dans un commit, avec le chantier actif et une entrée de journal qui dit la reprise ;
   - `git checkout -B claude/socle-roadmap-l-0016-drf6h3` ;
   - `git apply <copie>/tests-existants.diff`.

   La branche distante avance alors sans réécriture.
2. **La passe 2 de la revue**, sur la correction seule, selon les skills `socle-review` et `delegate-lot` : `socle review --since 381025a --batch L-0016`, produit dans un worktree où le diff des tests est appliqué. À éprouver :
   - le modèle de menace de la décision 89 : les clôtures au sens strict, un bloc jamais fermé, une citation, un bloc indenté, une sortie collée en texte que la tâche 91 laisse ;
   - l'ordre d'exécution avec des jalons qui alternent, et la fenêtre commune ;
   - le défaut injecté et son témoin : l'auto-test complet n'a pas tourné ;
   - le guide, la note de version, le point 17 du prompt de chess et l'architecture, au regard de la sortie réelle.
3. **Corriger les bloquants**, puis écrire le recul de la passe 2.
4. **Valider les dix tests par la variante légère (D-0134)** : la question dans la conversation, puis la réponse consignée en séance. `demande-brouillon.txt` en donne la liste, avec l'avant et l'après de chacun.
5. **À la réponse de Théo**, dans un même push : le lot, les dix tests et la réponse ; T-0088 close. Puis :
   - la CI verte ;
   - le lot clos (son recul, `fait`, `socle archive`), et le compact de `socle roadmap` collé au récap, dans un bloc de code ;
   - la fusion par l'agent (D-0092), puis la distribution vérifiée ;
   - puis L-0017 (T-0024), avant L-0015.
