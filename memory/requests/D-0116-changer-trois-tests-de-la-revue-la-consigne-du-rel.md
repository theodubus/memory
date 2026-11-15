<!-- socle: couche=demandes zone=publique -->
# D-0116 — Changer trois tests de la revue : la consigne du relecteur suit la règle du tri que vous avez validée, et une fonction morte se retire

> date : 2026-11-15

## Décision demandée

Autoriser l'agent à changer les valeurs attendues de trois tests de `tests/test_revue.py`, nommés plus bas : l'un suit la consigne nouvelle du relecteur, que votre règle du tri des constats du 14 novembre fait changer ; les deux autres suivent le retrait d'une fonction qui ne sert plus qu'eux.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le produit est ce moteur, que chaque projet équipé reçoit à l'installation et à chaque mise à jour ; ce dépôt s'en sert lui-même.

**Le chantier.** Avant les fonctions nouvelles du socle (la planification, puis la répartition du travail entre agents), l'agent finit la liste de corrections que vous avez fixée le 13 novembre, par lots : des groupes de sujets du backlog (la liste des sujets à traiter) livrés ensemble par une pull request. Le lot de ce jour, le cinquième sur six, porte sur la revue : avant de livrer un lot, l'agent le fait relire par un autre agent sans son contexte, le relecteur, qui cherche à le prendre en défaut et classe chaque constat. Le 14 novembre, vous avez validé une règle qui trie les constats non bloquants, et demandé qu'elle s'écrive dans le produit : dans le skill de la revue (la procédure écrite que l'agent suit), dans les instructions de chaque projet et dans la consigne que reçoit le relecteur. Ce lot l'écrit aux trois endroits.

**La question.** Un test vérifie le texte de cette consigne mot pour mot ; la consigne change, donc la valeur attendue du test aussi. La politique du projet interdit à l'agent de changer une valeur attendue sans un accord de vous qui nomme le test : celui du 14 novembre ne le nommait pas. Le même lot retire une fonction inutile, que deux autres tests appellent.

Les termes. Une **valeur attendue** : ce qu'un test exige du code ; la changer change ce que le test prouve. Un constat **bloquant** se corrige dans le lot (sa définition, inchangée, est dans la consigne plus bas). La **barre** du relecteur : les critères « Fait quand » des sujets du lot, les cases qui disent un sujet fait. Le **modèle de menace** d'un garde-fou (un contrôle ou un refus automatique) : ce qu'il arrête et ce qu'il laisse passer. L'**usage normal du projet** : celui du projet équipé. Un constat **infondé** : qui se révèle faux à la vérification. Un sujet **touché** par le lot : dont le lot modifie le fichier.

**1. La consigne du relecteur.** Votre règle, telle que vous l'avez validée : « un constat qui ne bloque pas va au backlog s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet [...]. **Écarté** : un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un cas jamais reproduit) dont l'effet est rattrapé, par un contrôle, la CI ou une erreur que l'agent voit aussitôt ; et un constat infondé. Une ligne du récap dit pourquoi chacun est écarté. » Les exemples sont les vôtres ; vous lisez donc chaque écart et sa raison dans le récap de l'agent.

La consigne aujourd'hui : « Classe chaque constat. **Bloquant** : il contredit un critère coché ou une décision citée, fait régresser ce qui marchait avant le lot, perd des données, ou contourne un garde-fou dans son modèle de menace ; un garde-fou que le lot pose ou change sans modèle de menace écrit est lui-même un constat bloquant. **Pour le backlog** : tout le reste, dont un contournement hors du modèle de menace, un critère que le lot ne coche pas, un défaut voisin, une amélioration. Seuls les bloquants se corrigent dans le lot. Rends deux listes numérotées, « Bloquants » puis « Pour le backlog », chaque constat avec son fichier et sa ligne, ce qui casse et comment le vérifier, et, pour un bloquant, ce qu'il contredit ; ou « aucun constat ». »

Demain, le « Bloquant » inchangé : « [...] **Pour le backlog** : un constat qui ne bloque pas, s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet ; un contournement hors du modèle de menace, un critère que le lot ne coche pas, un défaut voisin, une amélioration, jugés de même. **Écarté** : [votre texte, ci-dessus]. Seuls les bloquants se corrigent dans le lot. Rends trois listes numérotées, « Bloquants », « Pour le backlog » puis « Écartés », chaque constat avec son fichier et sa ligne, ce qui casse et comment le vérifier, pour un bloquant ce qu'il contredit, pour un écarté pourquoi ; ou « aucun constat ». » Le relecteur liste les écartés au lieu de les taire : l'agent vérifie chaque classement.

Dans `test_la_consigne_donne_la_barre_et_les_deux_classes`, renommé `test_la_consigne_donne_la_barre_et_les_trois_classes` : l'attente « **Pour le backlog** : tout le reste, dont un contournement hors du modèle de menace » devient « **Pour le backlog** : un constat qui ne bloque pas, s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet » ; « Rends deux listes numérotées, « Bloquants » puis « Pour le backlog » » devient « Rends trois listes numérotées, « Bloquants », « Pour le backlog » puis « Écartés » », et le repère « Rends deux listes », qui vérifie que la consigne précède le diff, « Rends trois listes » ; une attente s'ajoute, « **Écarté** : un constat exotique ». La consigne anglaise, pour les projets installés en anglais, se traduit de même ; aucun test ne l'attend mot pour mot.

**2. La fonction morte.** `sujets_fermes`, dans `engine/socle/review.py`, donnait les sujets clos que le lot touche. Depuis le 14 novembre, le dossier de la revue (le texte que le relecteur reçoit) donne tous les sujets touchés par une autre fonction, `sujets_du_lot` ; `sujets_fermes` ne sert plus que deux tests. Retirée, leurs attentes passent sur `sujets_du_lot`, la liste des sujets qui font la barre, avec les mêmes sujets attendus :

- `test_le_dossier_donne_la_consigne_le_diff_le_sujet_et_sa_decision` : le lot du test clôt un sujet fictif qui cite une décision fictive ; les deux attentes restent ce sujet et cette décision ;
- `test_un_sujet_encore_ouvert_n_est_pas_dans_le_dossier` : le lot du test ne change que du code, sans toucher le sujet ouvert ; l'attente reste « aucun sujet ».

Le premier sujet du lot change la base du diff que juge le dossier ; si la fonction rend ses listes autrement, les attentes en suivent la forme, mêmes sujets attendus.

## Éléments cités

- D-0112@c8501606 — votre accord du 14 novembre : écrire dans le produit la règle du tri des constats.
- D-0111@034d5e87 — votre décision du même jour, dans la conversation, d'où vient ce tri.
- ADR-0073@1e48220c — la décision de l'agent qui fixe la barre du relecteur et ses classes de constats.
- B-0223@2767e17b — le lot de ce jour, gardé au backlog comme un sujet qui réunit les siens.
- B-0214@8705b8ed — le sujet du lot qui relève la fonction morte.
- B-0213@9211c596 — le premier sujet du lot, qui change la base du diff du dossier.

Le suffixe après @ est l'empreinte de la version lue.

## Où regarder

- [Votre accord D-0112](https://github.com/theodubus/memory/blob/533daf38bae28c6e180b4f1753f71b09a8a14e05/memory/requests/D-0112-ecrire-dans-le-produit-les-deux-regles-qui-bornent.md), « Règle 1, la revue » : votre texte entier.
- [Les tests de la revue](https://github.com/theodubus/memory/blob/533daf38bae28c6e180b4f1753f71b09a8a14e05/tests/test_revue.py) : les trois tests nommés.
- [Le dossier de la revue](https://github.com/theodubus/memory/blob/533daf38bae28c6e180b4f1753f71b09a8a14e05/engine/socle/review.py) : `CONSIGNE_CLASSES`, la consigne, et `sujets_fermes`.

## Options

- Valider les deux : effort faible, les tests changent avec le code ; risque faible, chaque attente garde ce qu'elle prouvait ; réversible par une demande nouvelle.
- La consigne seule : elle suit votre règle ; `sujets_fermes` reste, sans emploi hors des tests, et le critère de B-0214 qui la vise reste ouvert.
- Refuser : la consigne garde « tout le reste » au backlog ; la règle n'est écrite que dans le skill et les instructions des projets, et le relecteur envoie au backlog les cas exotiques, que l'agent écarte lui-même.

## Conséquences

Si vous validez : l'agent change ces trois tests, et eux seuls, avec le code ; votre réponse, un fichier de la mémoire, part dans le même push. La consigne seule : seul le premier test change. Si vous refusez : rien de cela ne change, et l'agent note au lot que la consigne n'a pas la règle. Sans réponse : le reste du lot se livre sans ces changements, gardés dans un sujet du backlog.

## Recommandation

Valider. Vérifié : la consigne actuelle est le texte cité, et le test en attend les deux phrases mot pour mot (lecture du code et du test) ; `sujets_fermes` n'est appelée que par les deux tests nommés (recherche dans le dépôt). Supposé : que la fonction des sujets du lot gardera, après le premier sujet, une liste des sujets qui font la barre.

## Réponses possibles

- `valider` — les trois tests changent comme décrit, avec la consigne nouvelle et le retrait de `sujets_fermes`.
- `consigne-seule` — seul le premier test change, avec la consigne ; `sujets_fermes` reste.
- `refuser` — les trois tests gardent leurs attentes ; la consigne et la fonction restent telles quelles.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
