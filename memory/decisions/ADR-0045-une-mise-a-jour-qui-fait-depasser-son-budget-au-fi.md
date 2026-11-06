<!-- socle: couche=decisions zone=publique -->
# ADR-0045 — Une mise à jour qui fait dépasser son budget au fichier d'instructions le dit, sans exempter la section du socle du budget

> statut : acceptée · date : 2026-11-06 · source : B-0129@dfb8fb41 · lu : decisions@7f457f1f

## Contexte

La section du socle d'`AGENTS.md` se régénère à chaque mise à jour, et
peut grossir : de 330 octets environ avec ADR-0043@9be187f0. Une adoption
fixe le budget du fichier au millier d'octets supérieur à sa taille, et le
cliquet ne le laisse que baisser. Un projet proche de son budget passait au
rouge sur `memoire.budgets` dès la mise à jour, et le contrôle lui disait
d'« archiver dans le journal », ce qui ne vaut pas pour un fichier
d'instructions. B-0129@dfb8fb41 proposait deux voies : que la mise à jour
le dise, avec ce que l'humain peut faire ; ou que la section du socle soit
comptée à part du budget.

## Décision

- La mise à jour régénère la section comme avant. Si la section, en
  grossissant, fait passer au-delà de son budget le fichier d'instructions
  qui la porte (sans ce qu'elle a gagné, il tenait), l'installeur le dit
  dans son rapport : la taille, le plus bas des budgets qui le couvrent, ce
  que la section a gagné, et les deux issues, resserrer la partie propre au
  projet hors de la section, ou relever le budget par une demande validée.
  Le contenu qu'un CLAUDE.md apporte à AGENTS.md n'est pas la section ; un
  fichier qui dépassait déjà son budget n'en est pas accusé.
- Pour un fichier d'instructions, `memoire.budgets` donne ces deux mêmes
  issues, en octets comme en lignes, au lieu d'« archiver dans le
  journal ». Le commentaire du gabarit des garde-fous le dit aussi.
- La section du socle n'est pas comptée à part : le budget borne ce que
  l'agent lit à chaque session, section comprise, et l'en exempter
  assouplirait un garde-fou sans l'accord de l'humain.

## Conséquences

Un projet qu'une mise à jour fait déborder le sait dès le rapport de
l'installeur, avec son remède ; il reste rouge jusqu'à ce qu'il resserre ou
que l'humain relève le budget. Se défait en retirant l'alerte de
l'installeur et la branche du message dans `checks_memory.py`.
