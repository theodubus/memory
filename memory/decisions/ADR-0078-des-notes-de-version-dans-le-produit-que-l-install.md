<!-- socle: couche=decisions zone=publique -->
# ADR-0078 — Des notes de version dans le produit, que l'installeur donne à la mise à jour qui recopie le moteur

> statut : acceptée · date : 2026-11-14 · source : B-0151@adc00fd9, J-2026-11-10-H@a5473f3b, ADR-0053@5b55c0fa, ADR-0052@1e39f204, ADR-0077@1b7b9292, ADR-0033@44523582 · lu : decisions@9ecc00fd

## Contexte

Au passage du pilote au moteur nouveau, toutes ses empreintes de lecture
ont changé (ADR-0053@5b55c0fa) ; son agent l'a découvert en relisant avant
de citer, sans qu'aucune note ne l'ait prévenu (J-2026-11-10-H@a5473f3b).
Rien ne dit, à la mise à jour, ce qu'une version change pour un projet
installé (B-0151@adc00fd9) : ce dépôt l'écrit à la main pour chess, dans
un prompt qu'un projet tiers n'a pas. La version ne peut pas servir de
repère : elle n'a pas bougé d'une publication à l'autre depuis des semaines
(ADR-0077@1b7b9292, point 1). La mise à jour lit déjà le moteur installé
avant de le remplacer, pour ses adaptateurs (ADR-0052@1e39f204).

## Décision

1. **Les notes, dans le produit.** `engine/socle/CHANGES.md`, et sa
   version anglaise `CHANGES.en.md`, comme le guide : copiées avec le
   moteur, couvertes par son empreinte. Une entrée par changement qui
   touche un projet installé, sous un titre `## <identifiant> — <titre>` :
   l'identifiant est la date du changement et une lettre minuscule
   (`2026-11-14-a`), stable, jamais renuméroté ni repris ; les deux
   fichiers ont les mêmes, dans le même ordre, les plus récents d'abord.
   Son corps dit ce qui change, puis, dans un paragraphe qui commence par
   « À faire : » (« To do: »), ce que l'agent du projet doit faire, ou
   « rien ». Elles parlent la voix du produit (ADR-0033@44523582) : aucun
   renvoi à l'atelier.
2. **La comparaison par identifiants.** Avant de remplacer la copie du
   moteur que le projet a, l'installeur lit les identifiants de ses notes,
   dans l'une et l'autre langue ; après la copie, il donne les entrées de
   la copie nouvelle qu'elle n'avait pas, dans la langue du projet. Une
   copie sans notes, d'avant cette règle : toutes, en disant que leur date
   montre celles que le projet a déjà. Rien à une première installation,
   ni en mode amont, où le moteur est la source, ni quand le moteur n'est
   pas recopié, l'installeur lancé depuis le projet le gardant
   (ADR-0077@1b7b9292) : la copie en place est celle que les notes
   décriraient.
3. **Où l'agent les lit.** Dans la sortie de l'installeur, entières, entre
   ce qu'il a posé et l'audit, sous une ligne qui dit d'en faire ce que
   chacune demande. Pour la session suivante, quand l'humain a lancé la
   mise à jour dans son terminal : le message de commit que « Et
   maintenant » propose porte un second paragraphe qui nomme leurs
   identifiants et le fichier où les lire, et l'étape qui ouvre l'agent
   dit de les lui faire lire. Rien dans la mémoire du projet ni dans
   l'état : la mémoire est au projet, l'état se calcule, et le texte des
   entrées est déjà dans sa copie du moteur.
4. **La règle de l'atelier.** Un changement qui touche ce qu'un projet
   installé reçoit ajoute son entrée aux deux fichiers, dans le même
   travail ; `AGENTS.md` le dit parmi les règles propres à ce dépôt. Aucun
   contrôle ne l'exige : aucun ne sait dire quel changement touche un
   projet ; la revue du lot le juge.

## Conséquences

À la première mise à jour d'un projet installé avant cette décision,
l'installeur donne toutes les entrées, dont certaines décrivent ce qu'il a
déjà ; leur date le dit. Un test exige que les deux fichiers aient les
mêmes identifiants, uniques, chacun avec ce qu'il faut faire. Ce qui
reste supposé : que l'atelier écrive l'entrée de chaque changement ; une
entrée oubliée ne se voit qu'à la revue, ou chez le projet. Se défait en
retirant `notes_nouvelles` et son affichage de
`engine/socle/installer.py`, les deux fichiers, et la règle d'`AGENTS.md`.
