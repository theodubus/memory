<!-- socle: couche=decisions zone=publique -->
# ADR-0014 — Fuites, relecture et demandes privées : ce que l'humain a tranché

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-AA@d477e3ac · lu : decisions@b083d84f

## Contexte

Le cadrage laissait trois arbitrages sur les fuites de mémoire privée à
l'humain. Théo les a tranchés : la relecture avant publication reste au
choix de l'humain (D-0006@f08b0513), l'agent ajoute à la liste des termes
privés et seul l'humain en retire (D-0007@b1d5c5f6), le hook de l'agent
cherche aussi les fuites, en plus des hooks git et de la CI
(D-0008@3ad65a47). Il a demandé en outre que les demandes et leurs réponses
puissent devenir privées, sur sa décision.

## Décision

- **Relecture** : `[private] review` de la politique, `aucune`,
  `chaque-push` ou `lots`. Avec les deux dernières, le hook de l'agent et
  le hook git avant push refusent un push vers le dépôt public tant que le
  commit qui part n'a pas été relu. La relecture se dit par `socle relu` :
  l'humain lui-même, ou l'agent qui relaie son accord donné dans la
  conversation, avec son texte exact, comme une réponse (ADR-0006@3841810a). Elle
  vit dans le répertoire git commun, comme la trace des hooks. Les deux
  modes ne diffèrent que par le rythme que suit l'agent.
- **Termes privés** : un fichier texte de la zone privée, un terme par
  ligne, `re:` pour une expression régulière, recherche sans casse ni
  accents, par mots entiers. Ajouter est libre (cela durcit) ; retirer est
  refusé sans demande validée qui cite la liste et son empreinte nouvelle,
  sans nommer le terme. Un terme trouvé n'est jamais réécrit, seulement
  désigné par son rang.
- **Fuites** : trois étages. Le hook de l'agent sur ce qu'il ajoute hors de
  la zone privée, les commandes `git commit`, `git tag` et `gh`, et tout
  outil externe (pull requests, commentaires) ; un hook git sur le message
  de commit, pour tout agent ; la CI sur les fichiers publics modifiés et
  les messages des commits.
- **Demandes privées** : `[private] requests = true` ; publiques par
  défaut, pour que l'humain les lise là où il lit. Leurs réponses sont
  protégées comme les réponses publiques. En mode chiffré, GitHub n'en
  montre que le chiffré : l'agent les donne en entier dans la conversation.

## Conséquences

Une relecture relayée repose sur la bonne foi de l'agent qui la consigne,
comme une réponse relayée ; elle reste locale, donc la CI ne la voit pas.
Une validation privée en mode compagnon vit dans le dépôt privé : elle ne
peut pas couvrir un changement protégé du dépôt public, qu'une demande
publique doit valider. La recherche par mots entiers ne voit pas une
reformulation ; c'est la limite que le cadrage annonçait.

Pour défaire : chaque pièce se règle dans la politique (`review = "aucune"`,
`requests = false`) ; la liste des termes peut rester vide.
