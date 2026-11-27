<!-- socle: couche=demandes zone=publique -->
# D-0235 — Arbitrer le troisième retour de chess : sept besoins nouveaux dans JA-0006, quatre gênes en réserve, six écartées, B-0365 gardé sous condition, B-0370 satisfait par une ligne

> date : 2026-11-27

## Décision demandée

Arbitrer ce que le troisième retour de chess fait entrer dans le jalon en cours, mettre en réserve ou écarter : valider les douze points de la recommandation, en bloc ou avec des ajustements par numéro.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui permet de confier un projet de code à un agent d'IA sur la durée : mémoire, documentation, contrôles et demandes de décision à l'humain. Le moteur est son code. Chess, un moteur d'échecs en Rust, est le projet réel qui l'emploie et en rapporte les gênes.

**Le chantier.** Le jalon en cours met chess à jour (il reçoit la dernière version du socle, par un texte que tu donnes à son agent, le prompt de mise à jour), puis corrige ce que cette mise à jour montre. Chess a livré trois retours le 26 novembre ; les besoins des deux premiers sont clos. Le 26, tu as choisi pour le troisième une relecture critique suivie de ton arbitrage, plutôt qu'une règle d'entrée fixe ; le 27, de la faire maintenant, d'y juger aussi le tri de la réserve et la demande qui fait répondre deux fois, et de rattacher la mesure de chess au jalon « mesurer en usage réel ».

**La question.** La relecture est faite : chaque gêne est vérifiée dans le code du moteur et triée par le but du socle. Il reste à décider ce qui entre dans le jalon, ce qui attend en réserve, et ce qui s'écarte.

Les mots du socle : un besoin dit ce qui manque, une tâche le travail qui le sert, un lot les tâches menées et relues ensemble, en une session environ ; un jalon réunit des besoins, la réserve garde ceux d'aucun jalon, chacun avec sa raison. Un refus est un contrôle automatique, un hook, qui bloque l'agent jusqu'à ce qu'il corrige : sur une commande, un commit, ou la fin d'un tour (une réponse de l'agent). Le récap est le compte rendu de fin de réponse. Une consigne est une règle que tu as donnée, recopiée mot pour mot ; son empreinte, le suffixe `@…`, prouve que l'agent a lu la version citée. La passation est la note d'une session à la suivante ; l'état, ce que le socle calcule et montre à l'agent au démarrage. Les réveils de reprise sont deux rappels que l'agent programme pour reprendre seul si une limite d'usage le coupe.

Le retour mesure le coût du socle en appels d'outil, chacun relisant tout le contexte : sur 118 appels d'une séance de chess, au plus 40 % sont de la cérémonie ; les hooks de chess ont opposé 56 refus du 12 au 26 novembre. Le tri suit `docs/fabrication/but-et-tri.md` : une gêne entre si elle sert la mémoire, le contexte de l'agent, la vérification, ta décision ou le fonctionnement réel, si elle a été vue en usage réel, et si son coût est en proportion. Une gêne écartée revient si elle est revue.

## Éléments cités

- B-0367@1c32c3b1 — le besoin d'intégrer le troisième retour de chess, que cet arbitrage satisfait.
- T-0209@522e98c4 — la tâche de la relecture critique et de cette demande.
- JA-0006@503b25d5 — le jalon en cours : la mise à jour de chess, puis ses corrections.
- JA-0003@2b5fa986 — le jalon qui mesurera les refus et les appels, avant et après ces corrections.
- B-0365@183350f1 — la réserve que rien ne trie, et sa règle en trois moments.
- D-0213@8efe48de — ta validation de cette règle, le 26 novembre, à quinze lots.
- B-0370@422badb3 — une demande qui assouplit un contrôle sans nommer sa clé fait répondre deux fois.
- B-0368@602d20cc — un test qui rejoue la mise à jour de chess avant de lui donner son prompt.
- D-0217@e452fcf2 — ton choix d'une relecture critique et d'un arbitrage.
- D-0232@9956b489 — ton accord pour arbitrer maintenant, avant le code du tri de la réserve.
- D-0233@a0d356d9 — ton accord pour rattacher la mesure de chess au jalon de la mesure.
- D-0234@f47b43ab — ton accord pour juger la demande qui fait répondre deux fois ici.

## Où regarder

- [La relecture critique](https://github.com/theodubus/memory/blob/0555809fa9f3a5be36c1b4ec5743596029c1b01b/docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md) : pour chaque gêne, ce que le code confirme, le coût de la correction et la recommandation.
- [Le retour de chess](https://github.com/theodubus/memory/blob/975fe8fc75f15ec3d938770ae82135056c21b9af/docs/fabrication/chess/cout-et-frictions-2026-11-26.md), pour vérifier qu'aucune gêne n'est omise.

## Options

- **A. Valider en bloc.** Effort : sept besoins, environ 400 lignes de code et de tests, plus le tri de la réserve, soit quatre lots environ avant le prochain prompt de chess. Risque : les points 1 à 3 changent ce que trois contrôles laissent passer, dit à chacun ; leurs tests et un défaut injecté (un test qui vérifie que le contrôle attrape encore sa faute) les gardent. Réversible : un besoin s'abandonne avant son code.
- **B. Valider avec des ajustements par numéro**, par exemple « valider, sauf 6 en réserve ». Effort moindre : ne garder que les deux points qui pèsent le plus, 1 et 5, le reste en réserve jusqu'à la mesure de JA-0003, ferait deux lots environ. Risque : les autres gênes attendent. Réversible : une réserve se retrie.

## Conséquences

- **Si tu valides** : B-0367 se clôt ; les besoins retenus entrent dans le jalon avec leurs tâches, dans l'ordre du point 12 ; les réserves s'ouvrent avec leur raison ; les écartées vont au journal ; puis le premier lot commence.
- **Si tu refuses** : B-0367 reste ouvert, et l'agent te demande ce qui change.
- **Sans réponse** : aucune tâche n'est prête ; le tri de la réserve et la mise à jour rejouée attendent.

## Recommandation

Valider, soit ces douze points :

1. **Les liens du dernier message** : la fin de tour refuse un nom entre accents graves qui n'est pas un chemin du dépôt, dont ton interface ferait un lien mort. 20 refus sur 56, chacun un message de plus ; tu t'en es plaint (« Pourquoi tu répètes 2 fois le récap de fin ? »). Le refus donnera le chemin complet d'un nom qui désigne un seul fichier, et le message qui corrige n'aura plus à redire le récap. Laisse passer : ce message sans récap, quand le précédent en avait un. Environ 80 lignes.
2. **Trois refus qui savent leur correction** (4 refus) : une consigne citée sans empreinte reçoit l'empreinte dans le refus, et celle que l'agent vient d'écrire dans le même travail passe sans elle (laisse passer : rien qu'il n'ait sous les yeux) ; deux messages gagnent une ligne. Environ 40 lignes.
3. **Un commit de documentation titré « Correction »** est pris pour un correctif et refusé faute de test ; chess a dû le déplacer sur une autre branche. Un correctif qui ne touche que la documentation et la mémoire ne sera plus jugé (laisse passer : rien qu'un test prouverait). Environ 15 lignes.
4. **Une session neuve en retard sur sa passation** : chez chess, sur une copie vieille de trois heures, instructions comprises ; ici ce matin, sur un chantier actif périmé, sans autre suite qu'une lecture fausse que la passation a corrigée. L'état le dira d'abord. Environ 60 lignes.
5. **Clore une tâche en un geste** : environ huit commandes de mémoire pour une tâche de deux lignes ; une seule les fera, l'agent cochant toujours ses critères. Environ 150 lignes, cinq appels de moins par tâche.
6. **Les réveils de reprise**, armés à chaque réponse et retirés à sa fin (12 appels sur 118), resteront d'une réponse à l'autre ; un réveil sans objet coûtera une vérification et une ligne. Du texte, environ 40 lignes.
7. **Ta parole** : toute parole qui vaut au-delà d'une réponse devient une consigne, lue à chaque démarrage ; chess y a rangé une décision et une attente. Désormais, une règle de travail en consigne, une décision en décision, une attente en besoin bloqué. Environ 20 lignes.
8. **Le tri de la réserve** : ta règle du 26 novembre reste entière (une raison à la naissance, un tri à la clôture de chaque jalon, un signal après quinze lots), à cette condition sur sa mise en œuvre : ni appel ni refus de plus. Si elle ne se tient pas, l'agent te le demande.
9. **La demande qui fait répondre deux fois**, vue une fois : une ligne dans le contrat que l'agent lit en créant une demande, au lieu d'un contrôle ; rare et bénin.
10. **En réserve, quatre** : (a) un lot pour une seule tâche, que chess trouve lourd, la mesure le dira ; (b) le push sur `main` d'un dépôt local jetable, refusé deux fois comme une publication, une autre branche suffit ; (c) la revue inscrite au backlog avant le retour du relecteur, que la session pousse trop tôt, rien ne se perd ni ne fusionne ; (d) avancer la branche au démarrage, effet non vérifié, le point 4 dira si l'écart persiste.
11. **Écartées, six** : (a) le rangement fait par le hook de commit, que le point 5 couvre ; (b) ne refuser d'un script python que ses écritures, et non sa simple mention d'un fichier protégé : deux refus chez chess, un ici aujourd'hui, l'outil d'écriture de fichiers suffit, un contrôle au commit rattrape ; (c) trois refus de l'installeur, deux légitimes, un sans sa commande ; (d) trois refus non classés, sans donnée ; (e) ne réarmer les réveils que pour les longues réponses, que le point 6 couvre ; (f) signaler la copie périmée à l'hébergeur des sessions, hors du socle, à toi si tu le veux.
12. **L'ordre** : les refus et l'état (1 à 4), la clôture (5), les textes (6, 7, 9), puis le tri de la réserve et la mise à jour rejouée, avant le prochain prompt.

Vérifié : chaque gêne est confirmée dans le code, fichier et fonction cités dans la relecture ; la session en retard s'est reproduite ici, et cinq appels de réveil y ont précédé tout travail. Supposé : les tailles, et les gains, ceux d'une seule séance de chess.

## Réponses possibles

- `valider` — les douze points ; tes ajustements par numéro, s'il y en a, se consignent avec ta réponse.
- `refuser` — rien n'entre ; B-0367 reste ouvert.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
