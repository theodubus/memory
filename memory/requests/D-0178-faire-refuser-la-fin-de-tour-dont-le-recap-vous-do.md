<!-- socle: couche=demandes zone=publique -->
# D-0178 — Faire refuser la fin de tour dont le récap vous donne à supprimer une branche que GitHub n'a plus

> date : 2026-11-24

## Décision demandée

Choisir comment empêcher l'agent de vous demander, dans la ligne « Pour toi » du récap qui clôt chacun de ses tours de travail, de supprimer une branche que GitHub n'a déjà plus : un contrôle de fin de tour qui vérifie la branche sur GitHub (recommandé), une règle d'écriture du journal, ou rien.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, l'a déjà et recevra ce changement à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours corrige et stabilise le produit avant cette mise à jour. Son lot du récap et de l'état, un ensemble de tâches relues ensemble, rend justes les gestes, les actions, que l'agent vous donne à faire. Le 12, le 14 et le 18 novembre, vous avez relevé que l'agent vous demandait de supprimer des branches déjà supprimées ; le 18 au soir, l'état, le résumé que le socle calcule à chaque démarrage, a été corrigé : il demande à GitHub les branches qui existent encore avant de vous en donner une. Le 20 novembre, vous l'avez relevé une quatrième fois ; l'état, lui, ne donnait pas cette branche : sa correction tenait.

**La question.** Le 20 novembre, l'agent a repris la branche d'une entrée du journal, le registre daté où chaque session note ce qu'elle a fait, en ajout seul ; écrite la veille par la session d'avant, elle la disait « à supprimer après la fusion de la pull request ». Il l'a recopiée dans « Pour toi » sans la vérifier, malgré la consigne de le faire écrite au chantier actif, le fichier de la mémoire qui dit le travail en cours et vos consignes, qui y restent tant que vous ne les retirez pas. Le récap est écrit par l'agent, et aucun contrôle ne le juge sur ce point. Vos mots : « Pour la branche a supprimer ça fait plusieurs fois que tu me le demandes alors qu'elle etait deja supprimée, normalement le fait de check a deja été réglé mais visiblement pas correctement ».

**Le contrôle de fin de tour.** Un tour est le travail de l'agent entre deux de vos messages ; il se clôt par un récap, ce qui a été fait, puis deux lignes : « Pour toi », ce que vous seul pouvez faire ou décider, et « Ensuite », la suite proposée. Le hook de l'agent est l'ensemble des scripts que Claude Code, l'outil où l'agent travaille, lance seul à certains moments ; l'un d'eux, à la fin de chaque tour où l'agent a agi, relit son dernier message. Il le renvoie à l'agent, une fois, s'il manque « Pour toi » ou « Ensuite », s'il donne un lien que vous ne pourriez pas ouvrir, ou s'il cite une demande en attente sans son lien. Au second essai, il laisse conclure, et vous voyez un avertissement dans la conversation : il ne bloque jamais deux fois.

**La piste du contrôle, sa spécification.** Dans la partie « Pour toi » du dernier message, hors des blocs de code, chaque ligne qui parle de supprimer une branche (elle contient « supprim » et « branche » ; en anglais, « delete » et « branch ») est lue, sauf si elle parle d'une branche locale (« locale », « local »), qui n'est pas sur GitHub ; chaque nom écrit entre accents graves que git accepte comme nom de branche (préfixe `origin/` retiré) est cherché sur GitHub, par la même question que pose l'état depuis le 18 novembre (`git ls-remote --heads origin`, cinq secondes au plus), posée seulement si une telle ligne existe. Une branche que GitHub n'a plus fait renvoyer le message : « la branche que “Pour toi” donne à supprimer n'est plus sur l'origine : la retirer ». GitHub qui ne répond pas : rien n'est refusé, un avertissement le dit. Le calcul se place dans le code qui juge déjà les liens du message, à côté du contrôle du lien d'une demande citée ; le fichier du hook ne reçoit que les quelques lignes qui donnent la raison du refus. L'auto-test du socle, qui injecte des défauts connus et vérifie que chaque contrôle les attrape, reçoit le défaut (un récap qui donne une branche absente : renvoyé) et son témoin sain (une branche présente : accepté) ; une note de version.

**Son modèle de menace.** Il attrape la copie de bonne foi : d'une entrée du journal, d'un récap d'avant, du résumé d'un compactage (la conversation résumée quand elle devient trop longue), d'une référence à une branche supprimée que le clone garde tant qu'un `git fetch --prune` ne l'efface pas. Il ne voit pas une branche nommée sans accents graves, hors de « Pour toi », ou dans une phrase qui ne dit ni « supprimer » ni « branche » ; l'agent n'y est pas un adversaire. Un refus à tort, un nom entre accents graves qui n'est pas une branche sur une telle ligne, coûte une réécriture du récap, jamais un tour bloqué.

**Le hook de l'agent est fermé.** Depuis le 20 novembre, sur votre validation, il ne change que sur une preuve vue dans une session : un refus à tort qui a bloqué un vrai travail, ou un contournement écrit par un agent. Celle-ci est d'une troisième sorte : un geste faux qu'il vous a donné, quatre fois relevé. La valider ouvre le hook pour ce seul changement : la règle reste telle, et ne gagne pas de troisième sorte de preuve ; une autre exception demanderait une autre demande.

## Éléments cités

Plus bas : `JA-`, un jalon ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; `D-`, une demande ; `ADR-`, une décision écrite ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0311@110980d7 — le besoin, priorité haute : un récap ne peut plus vous donner une branche à supprimer que GitHub n'a plus.
- T-0125@f855e6c1 — la tâche qui pose cette demande.
- T-0126@45e8f1a7 — la tâche qui tiendra la piste que vous retenez.
- L-0024@fd20498d — le lot du récap et de l'état, en cours.
- JA-0005@06e926c0 — le jalon : le produit corrigé et stabilisé avant la mise à jour de chess.
- B-0193@047e5731 — le besoin d'avant, clos le 18 novembre : l'état ne vous donnait plus une branche que GitHub n'a plus.
- ADR-0090@8e880628 — la décision qui l'a corrigé : l'état demande à GitHub ses branches.
- ADR-0098@3081a5ed — la décision qui ferme le hook de l'agent, sauf preuve vue en session.
- D-0143@04eddcb5 — votre validation de cette fermeture, le 20 novembre.
- J-2026-11-20-Q@61928850 — votre remarque du 20 novembre, mot pour mot, et la vérification sur GitHub.
- J-2026-11-19-AK@f1c7709a — l'entrée du journal d'où l'agent a recopié la branche.

## Où regarder

- [Le besoin B-0311](https://github.com/theodubus/memory/blob/0bbf84c5134d9812482b68a77d5c555e8bea4aed/memory/backlog/B-0311-le-recap-donne-a-theo-une-branche-a-supprimer-que.md) : ce qui s'est passé, et les deux pistes.
- [La décision ADR-0098](https://github.com/theodubus/memory/blob/0bbf84c5134d9812482b68a77d5c555e8bea4aed/memory/decisions/ADR-0098-le-hook-de-l-agent-est-termine-on-n-y-touche-que-s.md), « Décision » : les deux preuves qui ouvrent le hook.
- [Le contrôle des liens](https://github.com/theodubus/memory/blob/0bbf84c5134d9812482b68a77d5c555e8bea4aed/engine/socle/links.py#L255), la fonction `problemes` : où le calcul nouveau se placerait, à côté du lien d'une demande citée.

## Options

- **Le contrôle de fin de tour** (`valider`, recommandé) : la spécification ci-dessus. Effort : une tâche, environ 150 lignes avec ses tests. Risque faible : au pire, une réécriture du récap, et cinq secondes d'attente quand « Pour toi » nomme une branche à supprimer. Réversible : retirer le calcul.
- **Une règle du journal** (`journal`) : le format de la mémoire (`FORMAT.md`) et les consignes de l'agent (`AGENTS.md`) disent qu'une entrée du journal ne donne aucun geste futur à l'humain, l'état seul les calculant. Effort : une tâche de texte. Risque : une règle, comme celle du chantier actif que l'agent a enfreinte ; la copie d'un récap d'avant ou d'un résumé reste possible, et les entrées déjà écrites restent, le journal ne se réécrivant pas. Réversible. Elle n'est pas proposée avec le contrôle : celui-ci attrape aussi la copie du journal.
- **Rien** (`refuser`) : la consigne du chantier actif reste seule, tant que vous ne la retirez pas. Aucun effort ; le geste faux peut revenir.

## Conséquences

Si vous validez : la tâche T-0126 écrit le contrôle, dans ce lot si votre réponse arrive pendant la session, sinon au prochain, avec son défaut injecté, son témoin et sa note ; B-0311 se ferme. Si vous répondez `journal` : T-0126 écrit la règle, et B-0311 se ferme sur ce choix. Si vous refusez : T-0126 s'abandonne en renvoyant à votre réponse, et B-0311 se ferme de même. Sans réponse : rien ne change ; le reste du lot continue, et T-0126 attend au lot suivant.

## Recommandation

Le contrôle de fin de tour. Vérifié : la question à GitHub fonctionne et se teste sans réseau (l'état la pose depuis le 18 novembre) ; le contrôle de fin de tour renvoie une fois, puis laisse conclure ; l'agent a recopié la branche d'une entrée du journal, et quatre relevés de votre part en neuf jours. Supposé : que les deux mots « supprim » et « branche » sur une même ligne suffisent à reconnaître le geste sans refus à tort, ce que les tests du contrôle éprouveront.

## Réponses possibles

- `valider` — le contrôle de fin de tour, écrit par T-0126 selon la spécification ci-dessus.
- `journal` — la règle d'écriture du journal, sans contrôle.
- `refuser` — rien ne change ; T-0126 s'abandonne.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
