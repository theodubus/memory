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
   borne. Le moteur ne connaît pas l'agent : la valeur est de la
   configuration, que le cliquet traite en budget (la relever assouplit,
   la baisser durcit ; absente, elle vaut 9 500).
2. **L'ordre.** a. L'état dérivé : les lignes qui demandent d'agir (les
   demandes, ce qui revient à l'humain, ce qu'il a écrit lui-même, les
   hooks, la mémoire privée, les lignes du hook) avant le backlog, dont la
   liste des prêts est la plus longue ; ses listes plafonnées à cinq
   commits non fusionnés et cinq sujets prêts. L'index des décisions en
   sort : l'essentiel tient dans les 2 000 premiers octets. b. Le chantier
   actif entier, public puis privé. c. Les faits par leur titre, publics
   puis privés, le statut dit quand il n'est pas « mesuré », avec la
   commande pour en lire un. d. Les dix dernières décisions, par date puis
   par numéro, la plus récente d'abord, le statut dit quand elle n'est pas
   acceptée, leur nombre et la commande de l'index entier, à lire avant
   toute décision de conception.
3. **La coupe.** Au-delà de la borne, des lignes entières se retirent
   depuis la fin : les décisions, puis les faits, le chantier actif en
   dernier recours ; un en-tête part avec la dernière ligne qu'il
   annonce. Une dernière ligne dit ce qui manque et la commande ou le
   chemin pour le lire : jamais en silence, jamais au milieu d'une ligne.
   L'état dérivé ne se coupe pas.
4. **L'empreinte de l'index sort de l'état.** `decisions@…` y prouverait
   la lecture d'un index qu'on n'a plus lu en entier ;
   `socle show --index decisions` la donne, `socle new adr` la pose.
5. **Le calibrage.** Le budget de `memory/active.md` descend de 6 000 à
   4 000 octets, ici et dans le gabarit : avec l'état et les titres, il
   tient sous la borne.

Pas de contrôle nouveau : la coupe se voit, et le budget du chantier actif
la prévient.

## Conséquences

La sortie du démarrage de ce dépôt passe de 25,7 Ko à 9,1 Ko, sans coupe
(J-2026-11-13-G@3bf0f1da). L'agent lit l'index entier, et les faits en entier, à la
demande : la section du socle d'AGENTS.md le dit. Une mémoire plus grosse
voit ses décisions puis ses faits coupés, et le sait. Les scénarios de
reprise du banc passent sur l'agent simulé ; D-0093 prévoyait de revenir
en arrière si les essais de reprise échouaient sur un agent réel.

Pour défaire : relever la borne (une demande validée), ou remettre
l'index et les faits entiers dans `parties_injectees` de
`engine/socle/state.py`.
