<!-- socle: couche=demandes zone=publique -->
# D-0027 — Rendre privé le dépôt d'essai, ou accepter d'y publier le moteur du socle

> date : 2026-10-14 · lu : decisions@c92d474a

## Décision demandée

Choisir si tu rends privé le dépôt d'essai `theodubus/tests` avant que j'y
pousse les cinq projets jetables, ou si tu acceptes que le moteur du socle y
soit publié, puisque chaque projet en contient une copie complète.

## Contexte

Tu as validé l'essai de la CI des cinq adaptateurs récents (JavaScript, Go,
Java, Ruby, PHP) dans un dépôt jetable public, `theodubus/tests`. Ma demande
disait que les projets ne contiendraient « qu'un petit module de calcul et
ses tests, rien du projet ». C'est faux, et je ne l'ai vu qu'en préparant le
push : l'installeur du socle copie le moteur entier dans chaque projet où il
s'installe (79 fichiers, environ 1,1 Mo : contrôles, hooks, adaptateurs,
gabarits, auto-test), et la CI du projet en a besoin pour tourner. Or le
dépôt `theodubus/memory`, où vit ce moteur, est privé. Pousser les projets
dans un dépôt public publierait donc le code du socle, ce que ta validation
ne couvrait pas.

Rien n'est parti : je n'ai pas ajouté `theodubus/tests` à ma session, ni
rien poussé. L'essai attend ta réponse.

## Éléments cités

- D-0025@ae4cfd76 — ma demande de l'essai, validée par toi (réponse
  `public`), dont la description du contenu poussé était fausse.
- B-0039@55928fbb — le sujet du backlog que l'essai doit clore : les étapes
  d'installation que chaque adaptateur ajoute à la CI n'ont jamais tourné
  sur GitHub.

## Où regarder

- [la copie du moteur par l'installeur](https://github.com/theodubus/memory/blob/2a40c785b7c8a7da508db6b03f693a24fcf33023/engine/socle/installer.py#L185-L204) :
  le moteur copié en bloc dans le projet installé.
- [ma demande de l'essai](https://github.com/theodubus/memory/blob/2a40c785b7c8a7da508db6b03f693a24fcf33023/memory/requests/D-0025-faire-tourner-sur-github-la-ci-que-posent-les-cinq.md) :
  la phrase « rien du projet », au premier point de ses options.

À vérifier : si le code du socle peut devenir public dès maintenant.

## Options

- **Rendre le dépôt privé** : dans les réglages de `theodubus/tests`
  (« General », tout en bas, « Change repository visibility »), tu le
  passes en privé ; je pousse alors les cinq projets comme prévu. Effort
  pour toi : une minute. Coût : les minutes de CI d'un dépôt privé comptent
  dans ton quota gratuit, environ 25 minutes pour cinq passages, une
  cinquantaine avec les reprises après correction. Risque nul pour le code.
  Réversible.
- **Le garder public, et publier le moteur** : je pousse tel quel ; le code
  du socle devient lisible par tous, sans licence (donc sans droit de
  réutilisation, mais copiable). Effort nul. Irréversible : même le dépôt
  supprimé, des copies peuvent rester (forks, caches, index).
- **Ne pas éprouver** : la CI des adaptateurs reste supposée, et B-0039
  reste ouvert. Effort nul ; le risque d'une CI rouge au premier push d'un
  projet de l'un de ces langages demeure. Réversible.

## Conséquences

- Si tu le rends privé : dès que tu me le dis, je pousse les cinq projets
  depuis une session à part, qui ajoute ce dépôt (celle-ci reste sur
  `memory` seul, comme tu l'as demandé), je lis chaque CI, je corrige les
  étapes fausses, puis je te dis quand tu peux supprimer le dépôt.
- Si tu acceptes de publier : la même chose, sur le dépôt public.
- Si tu refuses l'essai : B-0039 reste ouvert avec ta raison, et je passe
  à la suite de l'ordre validé.
- Sans réponse : rien n'est poussé ; je passe à ce qui reste en français
  dans un projet anglais, et l'essai attend.

## Recommandation

Le rendre privé. Vérifié : l'installeur copie le moteur entier dans le
projet ; `theodubus/memory` est privé (GitHub le dit) ; rien n'a été poussé.
Supposé : que tu ne veux pas encore publier le socle ; qu'un passage de CI
dure environ cinq minutes ; que mon accès GitHub couvre aussi un dépôt
privé de ton compte (sinon, l'ajout à la session échouera, et je te le
dirai).

## Réponses possibles

- `prive` — tu passes `theodubus/tests` en privé, puis tu me le dis ; j'y pousse les cinq projets.
- `publier` — tu acceptes que le moteur du socle soit publié dans le dépôt public ; j'y pousse les cinq projets.
- `refuser` — pas d'essai ; B-0039 reste ouvert.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
