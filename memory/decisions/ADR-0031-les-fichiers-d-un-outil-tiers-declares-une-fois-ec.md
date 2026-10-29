<!-- socle: couche=decisions zone=publique -->
# ADR-0031 — Les fichiers d'un outil tiers, déclarés une fois, échappent à tous les contrôles

> statut : acceptée · date : 2026-10-19 · lu : decisions@32a2bf3b

## Contexte

Mesuré à l'essai de cohabitation avec BMAD Method (F-0022@160bec31) : les
fichiers d'un outil installé dans le projet (ses skills, ses scripts)
étaient jugés comme ceux du projet. Ajouter BMAD faisait échouer quatre
contrôles sur ses seuls fichiers, et chacune de ses mises à jour l'aurait
refait ; l'adoption ne s'en sortait qu'en éteignant trois contrôles pour
tout le projet, son propre code compris. Les garde-fous excluaient
contrôle par contrôle (références, copies), et les tests ne s'excluaient
que dans l'adaptateur, fichier protégé. Théo veut un produit qui combine
le socle et BMAD, installés ensemble (J-2026-10-19-H@16d5a6c7).

## Décision

- Une seule liste de chemins tiers dans les garde-fous,
  `[thirdparty] paths`. Leurs fichiers sortent des listes que lisent tous
  les contrôles (fichiers, changements, renommages, à la tête comme à la
  base), de l'état, et du cliquet de mutation à l'installation.
- Y ajouter un motif assouplit : le cliquet des garde-fous l'exige d'une
  demande validée, comme une exclusion. Un motif qui couvrirait un fichier
  du socle, de la mémoire, la politique, un fichier protégé, AGENTS.md ou
  CLAUDE.md est écarté, et la configuration est en erreur.
- L'installeur reconnaît les outils qu'il connaît (BMAD Method : son
  dossier et ses skills) et déclare leurs chemins à l'installation, que
  l'humain lance ; à une mise à jour qui trouve un outil venu depuis, il
  les déclare et dit d'approuver l'assouplissement.
- Ce qu'un outil écrit pour le projet (les documents de BMAD) n'est pas
  tiers : le projet le possède, et les contrôles le jugent.
- Deux défauts injectés (un chemin tiers déclaré sans validation, un
  motif sur la mémoire) et un témoin sain (un outil déclaré et approuvé
  dont les fichiers fautifs passent la CI) l'éprouvent à l'auto-test.

## Conséquences

Le socle et BMAD s'installent ensemble sans contrôle éteint ni refus sur
les fichiers de BMAD, à l'installation comme à ses mises à jour. Le prix :
ce qui est déclaré tiers n'est plus vérifié du tout ; d'où la décision
humaine pour chaque motif, et le refus des motifs qui couvriraient ce que
le socle garde. Pour défaire : retirer la table et son filtre ; les
contrôles jugent de nouveau tout le dépôt.
