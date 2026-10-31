<!-- socle: couche=demandes zone=publique -->
# D-0054 — Étendre les réponses de base à la demande des questions de départ, que pose socle init

> date : 2026-10-31 · lu : decisions@4007cd0e

## Décision demandée

Choisir si la demande des questions de départ, que `socle init` pose dans
tout projet neuf, propose elle aussi les réponses de base `valider`,
`refuser` et `contexte-insuffisant`.

## Contexte

Théo a validé que toute demande propose les mêmes réponses de base,
`valider` prenant la recommandation (D-0053@a43f62b7). En l'appliquant, la
CI locale a montré une demande que le moteur pose lui-même : les questions
de départ, écrites par `socle init` dans tout projet installé, se
répondent par `defauts` (tous les défauts s'appliquent), `reponses` (le
texte de la réponse donne chaque réponse) et `contexte-insuffisant`. Le
pilote l'a reçue ainsi. La rendre conforme change ses réponses, et le test
`test_install_puis_init_par_la_ligne_de_commande` attend l'ancienne liste :
D-0053 ne le nommait pas, et changer sa valeur attendue revient à Théo
(politique, point 2). En attendant sa réponse, ces questions sont exemptées
de la règle, pour que le reste passe la CI ; rien n'est encore changé.

## Éléments cités

- D-0053@a43f62b7 — la décision de Théo : les réponses de base, les mêmes dans toute demande.

## Où regarder

- [le gabarit des questions de départ](https://github.com/theodubus/memory/blob/23c03d101be8b4ea97966e8acda3f4af4fedeb90/engine/socle/templates/starting-questions.md#L56) : ses trois réponses actuelles.
- [le test de l'initialisation](https://github.com/theodubus/memory/blob/23c03d101be8b4ea97966e8acda3f4af4fedeb90/tests/test_initialisation.py#L332) : la liste qu'il attend, qui changerait.

## Options

- **Option 1, les réponses de base aussi** : `valider` — tous les défauts s'appliquent (la recommandation) ; `reponses` — le texte de la réponse donne chaque réponse ; `refuser` — aucun défaut ne s'applique, chaque question reste ouverte au backlog ; `contexte-insuffisant`. L'exemption tombe, le test attend la nouvelle liste. Effort : un quart d'heure. Risque faible. Réversible.
- **Option 2, l'exemption** : les questions de départ gardent `defauts` et `reponses`, seule demande à faire exception. Effort : nul, c'est l'état actuel de la branche. Risque : le vocabulaire diffère pour la première demande de chaque projet. Réversible.

## Conséquences

- Si Théo valide : l'option 1 se fait dans la PR en cours, avec le test qui attend la nouvelle liste.
- S'il choisit l'option 2 : l'exemption reste, décrite dans le format.
- S'il refuse : comme l'option 2, sans la décrire.
- Sans réponse : l'exemption reste, et la PR attend cette réponse avant de s'ouvrir.

## Recommandation

L'option 1 : la première demande d'un projet est celle que l'humain lit en premier, et `valider` y dit déjà « les défauts », la recommandation.

Vérifié : seules ces questions, parmi les demandes que le moteur pose, échouaient ; la suite et le banc passent avec l'exemption.

Supposé : que `refuser` serve rarement ici ; il est proposé pour que la liste soit la même partout.

## Réponses possibles

- `valider` — l'option 1 : les réponses de base aussi, le test `test_install_puis_init_par_la_ligne_de_commande` attend la nouvelle liste.
- `exempter` — l'option 2 : les questions de départ gardent leurs réponses.
- `refuser` — rien ne change ; l'exemption reste, sans être décrite.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
