<!-- socle: couche=decisions zone=publique -->
# ADR-0071 — La sortie du démarrage bornée : l'état, le chantier actif, les titres des faits, les dix dernières décisions

> statut : acceptée · date : 2026-11-13 · source : B-0010@79c825c0, D-0093@333ad9d0, D-0107@ea525231, F-0014@24da316e · lu : decisions@8b5a2d9c

## Contexte

Le cadrage voulait un démarrage léger. Le 12 novembre, `socle state`
imprimait 28 Ko sur ce dépôt (25,7 Ko le 13) : l'état dérivé, l'index des
décisions entier (70 lignes, au milieu de l'état), le chantier actif et la
mémoire canonique entière. Claude Code ne remet entière à l'agent qu'une
sortie de hook de 10 000 caractères au plus (`fUA=1e4` dans son paquet
npm, une longueur de chaîne JavaScript, en unités UTF-16) ; au-delà, il la
range dans un fichier et n'en remet qu'un aperçu de 2 000 caractères. Le
chantier actif et les faits ne parvenaient donc pas à l'agent, ni ici ni
sur chess (B-0173@0ee3e459, J-2026-11-12-N@0d72078a).

Théo a validé la proposition 1 de D-0093 (« Je valide les éléments de la
dzmande sauf le point 7 ») : l'état au démarrage sous 10 Ko, les dix
dernières décisions et leur nombre, les faits par leur titre, le reste lu
à la demande. Il a passé le sujet en priorité haute (D-0107). F-0014
mesurait 4 Ko au plus sur les petits projets d'essai.

## Décision

1. **La borne.** `[startup] max_bytes` des garde-fous, 9 500 dans le
   gabarit et dans ce dépôt, et à défaut de la clé : la sortie entière du
   hook `SessionStart` (l'état, les lignes des outils de l'adaptateur en
   session cloud, l'avertissement des hooks git), sauts de ligne compris,
   en octets UTF-8, qui majorent les unités UTF-16 ; 500 de marge sous le
   seuil. `socle state` lancé à la main imprime la même chose sous la même
   borne ; `socle state --short` imprime l'état dérivé seul, entier. Le
   moteur ne connaît pas l'agent : la valeur est de la configuration, que
   le cliquet traite en budget (la relever assouplit, la baisser durcit ;
   absente, elle vaut 9 500).
2. **L'ordre.** a. L'état dérivé : les lignes qui demandent d'agir (les
   demandes, ce qui revient à l'humain, ce qu'il a écrit lui-même, les
   hooks, la mémoire privée, les lignes du hook) avant le backlog. L'index
   des décisions en sort : l'essentiel tient dans les 2 000 premiers
   octets. b. Le chantier actif entier, public puis privé. c. Les faits
   par leur titre, publics puis privés, le statut dit quand il n'est pas
   « mesuré », avec la commande pour en lire un. d. Les dix dernières
   décisions, par date puis par numéro, la plus récente d'abord, le statut
   dit quand elle n'est pas acceptée, leur nombre et la commande de
   l'index entier, à lire avant toute décision de conception. Les statuts
   se disent dans la langue du projet, et l'en-tête des décisions dit le
   nombre montré.
3. **Une part de la borne par partie.** L'état dérivé en a le quart
   (2 375 octets sous 9 500), le chantier actif 40 % (3 800), les faits
   22 % (2 090), les décisions 13 % (1 235) : `PARTS` de
   `engine/socle/state.py`. Ce qu'une partie laisse de sa part va, dans cet
   ordre, à celles qui dépassent la leur ; aucune ne prend sur la part
   d'une autre qui en a besoin.
4. **Ce qui borne chaque partie.** Dans l'état dérivé, chaque ligne tient
   en 1 000 octets (l'alerte des hooks non chargés, la plus longue des
   lignes fixes, en fait 953), dont les lignes du hook ; une ligne de la
   sortie d'un échec des outils, en 200 ; une ligne de commit en 80 ; le
   titre d'un sujet en 70. Chacune de ses listes est plafonnée, avec
   « … et N autre(s) » : cinq commits non fusionnés, cinq sujets prêts,
   cinq en cours ou bloqués, dix de priorité basse, quatre éléments de ce
   qui revient à l'humain, de ce qu'il a écrit lui-même, des demandes
   illisibles et des renvoyées. Une demande en attente ne se dit qu'une
   fois, sous ce qui revient à l'humain, avec son lien. Une ligne de fait
   ou de décision tient en 80 octets, son titre raccourci.
5. **La coupe.** Une partie au-delà de ce qui lui revient perd des lignes
   entières depuis sa fin, un en-tête avec la dernière ligne qu'il
   annonce ; le chantier actif ne se coupe ainsi qu'en dernier recours,
   quand il dépasse sa part et ce que les autres en laissent. Une dernière
   ligne dit, pour chaque partie coupée, sa taille pour sa part, ce qui en
   manque et où le lire (`socle state --short`, le fichier,
   `socle show --index decisions`) : jamais en silence, jamais au milieu
   d'une ligne. Chaque partie coupée paie ce que cette ligne dit d'elle ;
   son début se prend sur ce qui reste de la borne, à défaut sur la
   dernière partie coupée. La sortie tient sous la borne dans tous les
   chemins.
6. **L'empreinte de l'index sort de l'état.** `decisions@…` y prouverait
   la lecture d'un index qu'on n'a plus lu en entier ;
   `socle show --index decisions` la donne, `socle new adr` la pose.
7. **Le budget du chantier actif tient dans sa part.** Il descend de
   6 000 à 3 700 octets, ici et dans le gabarit : sa part, 3 800, moins
   son en-tête, permet 3 774 (`budget_actif_permis`). Un chantier actif
   dans son budget n'est donc jamais coupé, quoi que pèsent les autres
   parties. Un projet installé avant garde ses garde-fous à la mise à
   jour : quand leur budget du chantier actif dépasse ce que permet sa
   part (les 6 000 de chess et de JustCook), l'installeur le signale, avec
   la valeur qui tient, sans le réécrire. Pas de rétro-compatibilité
   exigée (J-2026-10-19-A@bb982c98), mais pas de coupe qui se répète sans
   être dite : la ligne de coupe le redit à chaque démarrage.

Pas de contrôle nouveau : la coupe se voit, et se dit.

## Conséquences

La sortie du démarrage de ce dépôt passe de 25,7 Ko à 9,1 Ko, sans coupe,
chaque partie mesurée (J-2026-11-13-G@c59b71b7). L'agent lit l'index
entier, et les faits en entier, à la demande, et ce qu'une ligne de coupe
désigne : la section du socle d'AGENTS.md le dit. Une mémoire plus grosse
voit couper la partie qui dépasse, elle seule, et le sait. Les scénarios
de reprise du banc passent sur l'agent simulé ; D-0093 prévoyait de
revenir en arrière si les essais de reprise échouaient sur un agent réel.

Pour défaire : relever la borne (une demande validée), changer `PARTS`,
ou remettre l'index et les faits entiers dans `parties_injectees` de
`engine/socle/state.py`.
