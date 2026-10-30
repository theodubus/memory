<!-- socle: couche=backlog zone=publique -->
# B-0093 — L'installeur fait exiger une revue que l'humain seul ne peut pas donner aux PR de son agent

> statut : ouvert · origine : J-2026-10-30-A · lu : backlog@3dbb481c

Les étapes qui suivent l'installation, et le guide, font exiger sur la
branche par défaut la CI et la revue des propriétaires du code. Mais un
agent en session cloud ouvre ses pull requests au nom de l'humain : les PR
#7, #8 et #9 de ce dépôt ont pour auteur `theodubus`. GitHub ne laisse pas
l'auteur approuver sa propre pull request ; un humain seul, propriétaire
unique du code, ne pourrait plus rien fusionner sans contourner sa règle.

Dire la revue des propriétaires utile quand un autre humain relit, et pour
un humain seul n'exiger que la CI. Vu en préparant l'installation du pilote.
