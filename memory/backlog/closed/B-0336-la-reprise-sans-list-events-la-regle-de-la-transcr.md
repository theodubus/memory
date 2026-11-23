<!-- socle: couche=backlog zone=publique -->
# B-0336 — La reprise sans list_events : la règle de la transcription laisse trois cas ouverts, et son test ne la prouve pas

> statut : fait · ref : J-2026-11-23-O · origine : J-2026-11-23-G · lu : backlog@4c7b474a

Relevé par la passe 1 de la revue de L-0010, le 23 novembre, sur la
règle que T-0040 a donnée au skill `socle-resume` : sans `list_events`,
le réveil lit la transcription locale de Claude Code. La règle est juste
sur la coupure (un enregistrement `quotaLimits`, son `timestamp`), mais :

1. Plusieurs refus peuvent se suivre (la coupure, puis un message de
   l'humain refusé, ou un réveil refusé par l'autre fenêtre) : la règle
   ne dit pas lequel marque la coupure. Pris au dernier, l'agent ne voit
   aucun texte tapé après lui et reprend par-dessus un « arrête » refusé.
   Ce cas ne joue que si un message refusé s'inscrit dans la
   transcription, ce qui n'est pas mesuré.
2. « Les `user` de texte tapé » n'a ni champ ni mesure. Le relecteur a
   vu, dans une transcription réelle, un message tapé porter
   `origin.kind` à `human`, le chargement d'un skill un `user` texte avec
   `isMeta`, et les notifications de tâche en `queue-operation`. La règle
   ne dit pas non plus comment lire la fin d'un fichier de plusieurs
   mégaoctets à peu de frais.
3. Une transcription qui existe sans le tour d'avant (un conteneur
   remplacé pendant une longue limite) ferait conclure « pas de limite »,
   là où la conversation aurait fait reprendre.

Le test (`tests/test_skills.py`,
`test_sans_list_events_la_transcription_locale_dit_la_coupure`) ne
vérifie que des mots et un ordre : il resterait vert avec « qui
précèdent » ou « le plus ancien », et rien ne relie les champs que cite
le skill à ceux que lit `engine/socle/consumption.py`. Le skill français
est à 10 octets de son budget de 8 000 : la règle précisée doit tenir
dedans.

## Satisfait quand

- [x] sans `list_events`, la reprise ne reprend jamais par-dessus un message tapé pendant la limite que la transcription montre, ni ne renonce sur une transcription qui n'a pas le tour d'avant, et un test le prouve
