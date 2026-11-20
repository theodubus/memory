<!-- socle: couche=demandes zone=publique -->
# D-0144 — Retirer l'obligation du recul au lot L-0006, garder l'historique des passes et le tri des constats sans la catégorie des formes du shell

> date : 2026-11-20 · forme : séance

## Question posée

Au lot L-0006, qui touche déjà les skills de revue et de lot : retirer l'obligation du recul (son paragraphe, les refus et contrôles qui l'exigent, les marques « même cause / cause nouvelle », l'arrêt par demande), garder l'historique des passes dans le lot (les bloquants de chaque passe), et garder le tri des constats bloquant / backlog / écarté sans la catégorie des formes du shell ?

Mesuré : depuis ADR-0084 (16 novembre), quatorze passes de revue sur neuf lots, quatorze reculs, tous « continuer », aucun arrêt ; ce soir, le recul a décrit la boucle du hook (« une ou deux entrées par lot ») et conclu « continuer ». Par construction, il pose la question à l'agent qui veut finir son lot, pour une passe de plus, et une boucle d'un lot à l'autre lui échappe. Son coût : un paragraphe d'au moins soixante mots à chaque passe et à chaque clôture, refusé par l'outil s'il manque, environ 120 lignes du moteur dans neuf modules et un fichier de tests, et il part dans chaque projet installé. L'historique des passes sert à une session neuve qui reprend un lot. Le tri des constats est ce qui permet à un lot de se terminer ; sa catégorie des formes du shell n'a plus d'objet avec ADR-0098, et D-0128 la retire déjà du produit. Rien ne remplace le recul : la protection contre la boucle est la règle de preuve d'ADR-0098.
