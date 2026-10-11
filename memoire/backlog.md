<!-- socle: couche=backlog zone=publique -->
# Backlog

Les sujets à traiter. Chacun a un statut (ouvert, en cours, bloqué, fait,
abandonné) et une origine ; un sujet clos porte la référence de ce qui l'a
clos, puis s'archive dans le journal (`python3 .socle/socle archive`).

## B-0004 — Jalon 9 : banc d'évaluation sur un agent réel

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Les six scénarios du cadrage et les métriques : part des défauts attrapés par
étage, faux positifs, durée de `verify`, coût en jetons du démarrage.

## B-0005 — Workflow de mutation hebdomadaire générique, et alerte quand il cesse de tourner

> statut : ouvert · origine : J-2026-10-10-D

Le verdict existe (`socle mutation-verdict`) ; manquent le gabarit de
workflow planifié et l'équivalent de `chess:tools/balayage-vivant.sh`, qui
voit un cliquet endormi par GitHub.

## B-0006 — Vérifier l'empreinte du moteur contre la version publiée en amont

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Aujourd'hui, la CI compare le moteur au verrou local. Le cadrage demande la
comparaison avec la version publiée, que le verrou seul ne garantit pas si
moteur et verrou changent ensemble.

## B-0008 — Les chemins qui n'existent que dans une rustine sont pris pour des liens morts

> statut : ouvert · origine : J-2026-10-10-F

25 cas sur chess, tous des lecteurs de sondes contenus dans les rustines de
l'attic. Une notation pour « chemin dans une rustine », ou une exclusion
déclarée par le projet.

## B-0009 — Adoption : importer l'existant que le socle sait lire

> statut : ouvert · origine : J-2026-10-10-F

Les plafonds de mutation de chess ont été repris à la main
(`docs/chess/mutation-caps.toml`). L'adoption pourrait proposer cette
reprise, et celle des tables « Ce qui tourne tout seul ».

## B-0010 — Calibrer les budgets de taille et de jetons du démarrage

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Question ouverte du cadrage. Les valeurs par défaut des garde-fous sont des
hypothèses ; chess donne un point de mesure (F-0005).

## B-0011 — Audit périodique de l'adaptateur

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Détecter un outil ou un langage nouveau dans le projet et émettre une
demande. Fréquence à décider (question ouverte du cadrage).

## B-0012 — Une copie non marquée d'une valeur liée n'est qu'un avertissement

> statut : ouvert · origine : J-2026-10-10-E

`docs.valeurs` refuse une valeur marquée fausse, mais ne fait qu'avertir sur
une copie non marquée de la valeur courante : elle pourrait être une
coïncidence. Mesurer les faux positifs avant de durcir.

## B-0016 — La docstring de memoire.py renvoie à un document de format qui n'existe pas

> statut : ouvert · origine : fichier:moteur/socle/memoire.py · lu : backlog@ad031cf1

Vu en écrivant le module des liens : la docstring du lecteur de la mémoire
dit que le format est décrit dans un document de `docs/` qui n'existe pas ;
c'est `moteur/socle/FORMAT.md` qui fait foi. Aucun contrôle ne lit les
chemins cités dans les docstrings du code.

## B-0017 — Deux fonctions calculent l'ancre GitHub d'un titre

> statut : ouvert · origine : J-2026-10-10-V · lu : backlog@5630c7c0

`liens.ancre`, écrite pour les permaliens, refait ce que fait déjà `slug`
dans `controles_memoire.py`, qui vérifie les ancres des liens de la mémoire.
Deux copies divergeront : n'en garder qu'une, que les deux modules
appellent.

## B-0018 — Le hook refuse un push vers la branche par défaut d'un dépôt local jetable

> statut : ouvert · origine : J-2026-10-10-W · lu : backlog@85e18aaf

Au jalon 6, le hook de l'agent a refusé `git push origin main` vers le
dépôt d'origine d'un projet jetable, un simple dossier local : la
politique (point 4) vise une publication, qu'un dépôt local n'est pas.
Ne refuser que si la destination est distante, ou garder le refus et le
dire dans sa raison ; à arbitrer, le refus large est le plus sûr.

## B-0020 — Une référence suivie d'un point ou d'une parenthèse est lue avec eux

> statut : ouvert · origine : J-2026-10-11-D · lu : backlog@c360de10

`memoire.references` lit une référence de commit suivie d'une parenthèse
fermante ou d'un point final avec cette ponctuation, et refuse un SHA
pourtant valide. Deux fois déjà, l'agent a dû
reformuler sa phrase. La fin d'une référence devrait exclure la ponctuation
finale, comme le font les liens Markdown.

## B-0021 — Une preuve de lecture recopiée d'une autre entrée du même fichier passe

> statut : ouvert · origine : J-2026-10-11-D · lu : backlog@8003fd30

Vu en corrigeant l'archivage : `memoire.lectures` ignore une citation déjà
présente dans la version de base du même fichier. Un sujet de backlog
nouveau qui recopie le `lu : backlog@…` d'un autre sujet passe donc, sans
avoir rien lu. Juger la citation par entrée plutôt que par fichier, comme
le fait désormais l'exemption des entrées déplacées.
