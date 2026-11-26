<!-- socle: couche=backlog zone=publique -->
# T-0199 — Sans notes dans la copie remplacée, l'installeur n'imprime en entier que celles d'après sa date

> statut : ouvert · origine : J-2026-11-26-AA · besoin : B-0361 · lu : backlog@dd11ac18

La date de la copie remplacée : celle du dernier commit qui l'a changée
(`git log -1 --format=%cs HEAD -- <copie>`). Une note datée d'avant
s'imprime par son titre, sous la ligne qui les compte ; les autres comme
aujourd'hui (`installer.texte_des_notes`, `notes_deja_lues`). Sans date
lisible, toutes comme aujourd'hui.

## Fait quand

- [ ] un test met à jour une copie commitée sans notes : une note datée d'avant son commit ne paraît que par son titre, une note du jour ou d'après en entier
