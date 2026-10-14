<!-- socle: couche=backlog zone=publique -->
# B-0060 — Une session de l'agent qui démarre hors de la racine du projet travaille sans ses hooks, et ne s'en aperçoit qu'au commit

> statut : ouvert · origine : J-2026-10-14-O · lu : backlog@c716992e

Demandé par Théo, à ne pas corriger maintenant. Son texte exact :

> Une session de l'agent qui démarre hors de la racine du projet travaille
> sans les hooks de l'agent, et ne s'en aperçoit qu'au commit.
>
> Constat (mesuré, voir J-2026-10-14-J et B-0058) : Claude Code ne charge ses
> hooks que depuis le dossier où la session démarre. La session précédente a
> redémarré le 12 oct. dans le dossier parent du dépôt et a travaillé un jour
> et demi sans hooks de l'agent : ni le filtre des commandes (qui refuse
> force-push, push sur la branche par défaut, écriture des fichiers
> protégés), ni les contrôles de fin de tour, ni l'état au démarrage.
> Supposé : une session cloud qui compte plusieurs dépôts démarre dans leur
> dossier parent. Mêmes effets si l'on lance Claude Code depuis un dossier
> parent, ou si le projet est un sous-dossier d'un dépôt plus grand.
>
> Déjà couvert depuis B-0058 (commit c103b9f) : la CI refuse un commit
> d'agent sans aucun passage du filtre depuis le commit précédent, et le
> hook commit-msg l'annonce. Mais c'est tardif, et le remède écrit (« ouvrir
> la session dans le dépôt du projet ») n'est pas toujours possible.
>
> Corrections proposées :
> 1. Détecter dès le début : socle state, lancé sous un agent (variable
>    CLAUDECODE) alors que la trace n'a aucun SessionStart pour la session
>    courante (CLAUDE_CODE_SESSION_ID), affiche en tête un avertissement
>    clair : les hooks de l'agent ne sont pas chargés.
> 2. Refuser plus tôt : le hook git pre-commit, qui tourne toujours, refuse
>    localement un commit d'agent sans passage du filtre depuis le commit
>    précédent, au lieu du seul avertissement de commit-msg.
> 3. Consigne dans le gabarit AGENTS.md (et la section du socle de ce
>    dépôt) : si l'état n'a pas été injecté au démarrage, les hooks ne sont
>    pas chargés ; le dire à l'humain avant tout travail, et ne rien pousser.
> 4. Le message de remède (commit-msg, CI, état) distingue les cas :
>    relancer la session depuis la racine du projet ; ou, dans une session à
>    plusieurs dépôts, ouvrir une session sur le dépôt seul. L'agent n'écrit
>    jamais lui-même un réglage de Claude Code pour rétablir ses hooks : c'est
>    ce qui a été fait le 14 oct. et désavoué (J-2026-10-14-J).
>
> Chaque contrôle nouveau a son défaut injecté et son témoin sain dans
> l'auto-test.
