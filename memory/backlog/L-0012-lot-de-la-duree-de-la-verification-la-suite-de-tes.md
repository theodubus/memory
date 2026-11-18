<!-- socle: couche=backlog zone=publique -->
# L-0012 — Lot de la durée de la vérification : la suite de tests sur plusieurs cœurs, la durée des étapes rapides dite et sous un seuil

> statut : en cours · origine : J-2026-11-16-I · après : L-0013, T-0044, T-0045 · lu : backlog@c0a47b1b · ancien : B-0266

Placé par Théo juste après L-0011, avant L-0005 (J-2026-11-16-I) :
`verify --fast` dure près de douze minutes sur un seul cœur, et chaque
lot en paie le prix (chaque push de plus de dix minutes, un implémenteur
qui ne finit pas sa vérification, le cache d'un sous-agent réécrit à
chaque attente). Ses deux sujets touchent la même étape, que juge une
seule revue : B-0257, la suite de tests de ce dépôt sur plusieurs cœurs,
dont le changement de `.socle/adapter.toml`, protégé, passe par une
demande à Théo ; B-0258, la durée de chaque étape dite et soumise à un
seuil, dont la spécification se soumet à Théo avant son code.

## Revues

### Passe 1 — 2026-11-17

Commits : cac8a20..8520f6a

- Bloquant : les liens de D-0130 sur un commit que la passation a réécrit, jamais poussé
- Bloquant : le point 3 de la spécification promet un avertissement en fin de tour et à l'envoi, que la marque des étapes déjà passées rend muet
- Bloquant : le seuil, un garde-fou nouveau, sans modèle de menace
- Ouvre : B-0281, T-0066, T-0067, T-0068

Recul : première passe, sans précédente à comparer ; ses trois bloquants avaient trois causes distinctes (un lien sur un commit que la passation a réécrit, une promesse de la spécification que la marque des étapes déjà passées rendait muette, un garde-fou nouveau sans modèle de menace), toutes corrigées dans D-0130 avant la réponse de Théo. Les entrées qu'elle ouvre, B-0281 et ses tâches sur le lanceur, puis B-0282, un défaut voisin du cliquet, prolongent ou côtoient ce que le lot ferme sans le refaire : elles ne sont pas de même nature que B-0257 et B-0258. Les lots clos qui ont touché les mêmes fichiers (le moteur, l'auto-test, le guide) ont ouvert des tâches du hook et de la revue, jamais une entrée sur la durée de la vérification. La passe 2 sera différente : elle juge le code de la spécification validée, depuis 8a7053c, et non plus la spécification. Décision : continuer

### Passe 2 — 2026-11-18

Commits : 8a7053c..b38e021

- Bloquant : un passage complet lancé par la fin de tour ou l'envoi garde sa trace au-delà du seuil sans dire l'avertissement à personne · cause nouvelle
- Bloquant : `nan` écrit librement au seuil, puis relevé sans demande, le cliquet comparant `vb > va` · cause nouvelle
- Ouvre : B-0283, que le sous-agent de la correction a trouvé ; le même trou du cliquet sur des clés d'avant le lot, constat pour le backlog, se ferme par la correction du second bloquant, la comparaison étant commune

Recul : les deux bloquants de la passe 2 ont des causes nouvelles, selon le relecteur, mais le premier voisine avec le deuxième de la passe 1 : deux fois, ce que l'agent lit d'un hook a été supposé au lieu d'être suivi jusqu'à sa sortie. Les entrées ouvertes (B-0282, B-0283) sont des trous du cliquet des garde-fous, de nature différente des besoins clos (la durée, le lanceur) : poser une clé au cliquet révèle ses voisines, sans que le lot les refasse. Les lots clos qui ont touché les mêmes fichiers ont ouvert des entrées du hook, du backlog et de la revue, aucune du cliquet. La passe 3 sera différente : elle ne relit que la correction, b6824ef, et éprouve chaque sortie des deux hooks jusqu'à ce que l'agent ou l'humain en reçoit, et chaque valeur non finie du cliquet. Décision : continuer

### Passe 3 — 2026-11-18

Commits : 90e63f6..3c76f83

- Bloquant : la fin de tour qui bloque pour un autre contrôle ne dit le seuil dépassé qu'à l'agent, dans sa raison, jamais à l'humain · même cause
- Ouvre : B-0284

Recul : le bloquant de cette passe a, selon le relecteur, la même cause que le premier de la passe 2 : une sortie de la fin de tour dont on a supposé ce qu'elle dit, au lieu de la suivre jusqu'à l'humain ; le deuxième bloquant de la passe 1 le voisinait déjà, mais c'est la première passe où le relecteur la voit revenir, et la règle d'arrêt en veut deux de suite. Cette fois, chaque sortie de la fin de tour a été éprouvée jusqu'à l'humain par le relecteur, réussie comme bloquée, et le test de la correction fait échouer la fin de tour par un rapport en échec, non plus par un rapport vide qui réussit toujours : il ne reste pas de sortie non suivie. L'entrée ouverte, B-0284, le délai du hook de fin de tour, est une limite du modèle de menace de B-0258, que le lot ferme, pas une régression ; les lots clos qui ont touché les mêmes fichiers (le hook, le moteur, l'auto-test) ont ouvert des entrées du hook de l'agent et de la revue, aucune sur les sorties de la fin de tour. La correction tient en quelques lignes, sans conception nouvelle : le skill de la revue ne demande pas de passe de plus, il ne reste aucune tâche au lot, qui se clôt. Décision : continuer
