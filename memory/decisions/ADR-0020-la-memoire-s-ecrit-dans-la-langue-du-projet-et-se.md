<!-- socle: couche=decisions zone=publique -->
# ADR-0020 — La mémoire s'écrit dans la langue du projet et se lit dans toutes

> statut : acceptée · date : 2026-10-11 · source : J-2026-10-11-P@f1c17ee1 · lu : decisions@4b3a1dc0

## Contexte

Théo veut pouvoir tenir la mémoire d'un projet en anglais, ou dans une
autre langue (B-0031@e912fd95). Tout le format était en français : champs
et statuts des entrées, en-têtes, sections des demandes, gabarits. Les
chemins, eux, sont déjà en anglais pour tous (ADR-0018@61948166) : ce sont
des identifiants, hors de ce sujet. Une mémoire est en ajout seul : ses entrées
gelées gardent les mots avec lesquels elles ont été écrites.

## Décision

La politique dit la langue de la mémoire (`[memory] language`, `fr` par
défaut, ou `en`), choisie à l'installation. Le moteur raisonne sur des clés
internes, celles du format d'origine ; un module unique tient, par langue,
le mot écrit de chaque clé.

La lecture accepte les mots de toutes les langues, quelle que soit celle
du projet. L'écriture suit la langue du projet : `socle new`, les gabarits
de l'installeur, la section du socle d'AGENTS.md, l'approbation, la
bascule, l'archivage, les lignes attendues du récap.

Pas de migration des mots-clés : elle réécrirait des entrées gelées, et la
lecture de toutes les langues la rend inutile. Un projet qui change de
langue garde ses anciennes entrées telles quelles. Les messages du moteur
restent en français pour l'instant.

## Conséquences

Une mémoire peut mêler deux langues, sans que rien ne casse : un contrôle
ne voit que les clés internes. Ajouter une langue, c'est ajouter ses mots au
module et ses gabarits (`<nom>.<langue>.md`). Le format documente la table
des mots, qu'un test garde alignée sur le module. Un défaut injecté en
anglais prouve qu'un contrôle juge encore une entrée anglaise.

Pour défaire : retirer `[memory] language` de la politique, et le projet
écrit de nouveau en français ; ses entrées anglaises restent lisibles.
