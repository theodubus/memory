# Les allégements du 18 novembre

Cinq propositions faites à Théo, le 18 novembre, dans la session qui a mené le lot L-0016, et validées par lui dans la conversation. Elles sont écrites ici telles qu'il les a lues, pour que la décision qui les consigne désigne ce texte et non un souvenir de la conversation (la proposition 4).

## D'où elles viennent

L-0016 corrigeait le format de `socle roadmap`. Il a consommé 75 % de la fenêtre de cinq heures avant même sa seconde revue. Théo, mot pour mot : « L0016 était un correctif de format de roadmap, je comprends pas pourquoi il a consommé 75% d'une session / Et la tel que c'est parti j'ai l'impression que L0017 va être pareil alors qu'en soit c'est juste le fait de check les branches github avant de demander de supprimer / Est ce que c'est juste un constat ponctuel ou est ce qu'il y a une lourdeur non nécessaire superflue avec le fonctionnement du socle ? »

Les mesures de la session, sur la fenêtre de cinq heures, de 1 % à 75 % :

| Étape | Points | Jetons |
| --- | --- | --- |
| L'implémentation, par un sous-agent | environ 30 | 328 000, 26 minutes |
| La passe 1 de la revue, par un relecteur sans contexte | environ 31, avec la ligne suivante | 216 000 |
| La correction des deux bloquants, par un sous-agent neuf | (comprise ci-dessus) | 247 000 |
| L'orchestration | environ 5 | |
| La passation, et la réponse sur les branches | environ 8 | |

Repère : un sous-agent coûte environ 7 à 9 points de la fenêtre par 100 000 jetons.

Une part tient au lot lui-même. L-0016 rattrape L-0014, construit sur une spécification qui avait perdu ses exemples (B-0286). L'un des deux bloquants vient d'un choix de l'orchestrateur. Une autre part tient au fonctionnement du socle :
- le coût fixe d'un sous-agent ou d'un relecteur neuf, quelle que soit la taille du lot ;
- les obligations qui s'empilent sur un lot ;
- le circuit des valeurs attendues ;
- le seuil de 60 % qui coupe un lot en plein milieu ;
- le bruit dans la conversation qui orchestre.

## Les propositions

### 1. Un circuit court pour les petits lots

- **Aujourd'hui.** Un sous-agent implémente chaque tâche, sauf un changement de quelques lignes. Ensuite, un relecteur sans contexte reçoit le dossier complet de `socle review` : le diff, les entrées du backlog et les décisions citées. Il a pour consigne d'explorer le dépôt et d'éprouver le code. Chacun relit d'abord les instructions, les skills et le code : 200 000 à 300 000 jetons, soit 15 à 30 points, même pour dix lignes.
- **Ce qui changerait.** Sous un seuil (par exemple moins de 150 lignes de code et de tests), l'orchestrateur implémente lui-même. Le relecteur reçoit un dossier court : le diff, les critères des tâches, et la consigne de juger le diff sans explorer au-delà des fichiers touchés.
- **L'exception.** Un lot qui touche un garde-fou, ou un format que d'autres parties du socle lisent, garde la revue complète.
- **Ce que ça économise.** Le sous-agent qui implémente (10 à 20 points sur un petit lot), et une bonne part de la relecture.
- **Ce qu'on risque.** Le relecteur voit moins. Le bloquant du récap de L-0016 n'a été trouvé que parce que le relecteur a lu le code du hook, hors du diff : d'où l'exception.
- **Qui décide, et sa mise en œuvre.** Théo, parce que c'est réduire la revue adversariale qu'il a voulue. Elle passe par deux skills du produit et leurs copies protégées.

### 2. Les tests qui lisent un format validé

- **Aujourd'hui.** Changer la valeur attendue d'un test exige une validation de Théo qui le nomme. Sa règle du 12 novembre (J-2026-11-12-F) demande une demande dans le dépôt, relue à froid par un sous-agent, poussée, son lien donné, jamais une question dans la conversation. Pour L-0016 : dix tests, une demande à écrire, une relecture à froid (mesurée à 130 000 jetons, environ 10 points, B-0197), un aller-retour, et des tests gardés hors des commits.
- **Ce qui changerait.** Quand le changement est mécanique (des tests qui lisent un format que Théo vient de valider), la demande garde sa liste des tests, avant et après, sans relecture à froid.
- **La variante légère.** L'agent pose la question dans la conversation, en nommant chaque test, et consigne la réponse mot pour mot en décision de séance. Le contrôle l'accepte, puisque la décision nomme les tests.
- **Ce que ça économise.** 10 à 15 points par occurrence, et l'attente : le lot se livre dans la même session.
- **Ce qu'on perd.** Le document de contexte relu à froid. La trace reste : chaque test est nommé, et la réponse est consignée.
- **Qui décide, et sa mise en œuvre.** Théo, parce que c'est sa règle. Elle tient en quelques lignes de deux skills.

### 3. Le hook de fin de tour ne recopie plus tous les échecs

- **Aujourd'hui.** Quand les tests échouent en fin de tour, le hook recopie toute la sortie : environ 10 000 jetons de traces, deux fois dans cette session. Chaque étape suivante de la conversation les relit.
- **Ce qui changerait.** Le hook donne le nom des contrôles en échec, la première ligne utile de chaque test en échec, et la commande qui montre tout.
- **Ce que ça économise.** Quelques points par session où des tests échouent en fin de tour (non mesurable sans T-0033).
- **Ce qu'on risque.** Rien sur le fond : le contrôle bloque toujours, et l'agent relance la commande s'il veut le détail.
- **Qui décide, et sa mise en œuvre.** L'agent, parce que c'est réversible. Elle tient dans un petit lot.

### 4. Une décision prise en séance garde ce qu'elle approuve (B-0286)

- **Aujourd'hui.** Le 16 novembre, Théo a validé dans la conversation une proposition avec ses exemples. La décision n'a consigné que la question et sa réponse. Le besoin a recopié la proposition sans ses exemples, L-0014 a construit le mauvais format, et L-0016 le rattrape pour plus d'une fenêtre.
- **Ce qui changerait.** Avant de consigner la validation, l'agent écrit la proposition telle quelle dans le dépôt, et la décision pointe vers elle avec son empreinte. Les tâches qui l'implémentent la citent, et le relecteur la reçoit.
- **Ce que ça économise.** Des lots de rattrapage entiers : rare, mais le plus gros poste quand ça arrive.
- **Qui décide, et sa mise en œuvre.** L'agent. Elle passe par le skill des demandes, et peut-être un refus de l'outil quand une décision approuve un texte qu'elle ne désigne pas.

### 5. Estimer le coût d'un lot avant de le lancer

- **Aujourd'hui.** Les seuils (60 % de la fenêtre de cinq heures, 85 % de la semaine) ne se vérifient qu'avant chaque lancement de sous-agent. L-0016 a démarré à 1 % et a été coupé à 67 %, en plein milieu : une passation d'environ 8 points, plus le rechargement dans la session suivante.
- **Ce qui changerait.** À l'annonce d'un lot, l'agent estime son coût à partir des mesures (sous-agent, relecteur, demande). S'il ne tient pas dans ce qui reste, il le découpe, commence par un lot plus petit, ou attend la remise à zéro. T-0037 (dans L-0009) va déjà dans ce sens, au niveau du sous-agent seulement.
- **Ce que ça économise.** Les passations en milieu de lot.
- **Qui décide, et sa mise en œuvre.** L'agent. Elle avance T-0037 et l'étend au lot.

Hors des propositions : le guide en deux langues, les notes de version et le prompt de chess sont des exigences du produit, et leur coût reste modeste.

## La réponse de Théo

Mot pour mot : « 1. Et tout faire faire par l'orchestrateur serait il pertinent ? A la base j'avais voulu des sous agents pour économiser du contexte justement et la je vois que ça en coute / C'est quand meme pertinent les sous agents tout court ? (Pour l'implementation j'entends, pas la relecture a froid qui elle a besoin d'un sous agent pour etre a froid) / Si oui alors je valide le 1 dans sa forme actuelle / 2 validé avec la variante légère / 3 validé / 4 validé / 5 validé »

## La réponse de l'agent sur les sous-agents qui implémentent

**Oui, ils restent pertinents, mais pas toujours.** C'est ce que trace le seuil de la proposition 1.

- **Pourquoi la conversation qui orchestre coûte.** Chaque étape de la conversation relit tout son contexte. La mise en cache en réduit le prix sans l'annuler.
- **Ce qu'un sous-agent épargne.** Ce qu'il lit et essaie pour implémenter reste hors de cette conversation, qui ne reçoit que son compte rendu, quelques milliers de jetons. Les 328 000 jetons de T-0088 sont surtout le travail lui-même : 141 appels d'outils pour lire le code, écrire et relancer les tests. L'orchestrateur aurait fait ce même travail. Il l'aurait ensuite gardé dans son contexte, relu à chacune de la soixantaine d'étapes qui ont suivi : la revue, sa correction, la passation.
- **Son coût fixe.** Il part à froid : les instructions, la tâche et le code qu'il doit comprendre, avant d'écrire une ligne.
- **La règle qui en sort.** Pour une tâche de quelques dizaines de lignes, ce coût fixe dépasse ce qu'il épargne : l'orchestrateur la fait lui-même. Pour une tâche plus grosse, suivie de nombreuses étapes, le sous-agent épargne. Avec un lot par session, la session est elle-même un contexte neuf : un lot d'une seule tâche moyenne peut être implémenté par la session, puis relu par un sous-agent.
- **Ce qui reste à mesurer.** Le seuil se mesure (T-0033, proposition 5) plutôt que de rester à 150 lignes.

Sa condition, « si oui », est remplie : la proposition 1 est validée dans sa forme actuelle.

## Ce qui s'ensuit

Les besoins et les tâches de ces cinq propositions s'ouvrent au backlog après l'intégration de la passation de L-0016 (son dossier, retiré à l'intégration : J-2026-11-18-S) : avant, ils prendraient les numéros que portent déjà ses correctifs.

La variante légère de la proposition 2 vaut dès maintenant comme consigne. Elle remplace, pour un changement mécanique de valeurs attendues, la règle du 12 novembre. Les dix tests de L-0016 se valident ainsi : une question dans la conversation qui les nomme, et la réponse consignée en séance.
