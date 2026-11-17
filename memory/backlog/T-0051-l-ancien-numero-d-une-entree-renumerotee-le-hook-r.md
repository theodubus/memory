<!-- socle: couche=backlog zone=publique -->
# T-0051 — L'ancien numéro d'une entrée renumérotée : le hook refuse sa mention dans un fichier neuf en le disant inventé, et socle url ne le résout pas

> statut : ouvert · origine : J-2026-11-16-V · besoin : B-0265 · lu : backlog@0c8ca830

Relevé par la revue du lot L-0013, passe 1 (J-2026-11-16-V), constat 1
pour le backlog. Un ancien numéro (`ancien : B-NNNN`, ADR-0083) se résout
dans `socle show` et `memoire.references`, mais le hook de l'agent
(`engine/socle/hooks.py`, vers la ligne 382) refuse sa mention dans un
fichier neuf avec le message d'un identifiant inventé (« `B-0224` … ne
désigne aucune entrée de la mémoire »), et `socle url B-0224` répond
« aucune entrée » (`engine/socle/links.py`, vers 116). Usage normal :
l'agent de chess qui reprend un numéro de son journal. Le livrable, un
commit : le hook nomme l'identifiant actuel de l'entrée au lieu de la dire
inventée, et `socle url` résout l'ancien numéro.

## Fait quand

- [ ] le hook, devant un ancien numéro dans un fichier neuf, nomme l'identifiant actuel de l'entrée, et un test le montre
- [ ] `socle url` donne le lien de l'entrée actuelle pour un ancien numéro, et un test le montre
