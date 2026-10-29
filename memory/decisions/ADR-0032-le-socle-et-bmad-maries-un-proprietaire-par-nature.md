<!-- socle: couche=decisions zone=publique -->
# ADR-0032 — Le socle et BMAD mariés : un propriétaire par nature d'information, une seule façon de consulter l'humain

> statut : acceptée · date : 2026-10-19 · lu : decisions@54148801

## Contexte

Le socle et BMAD Method s'installent ensemble (ADR-0031@ded211d6), et la
personnalisation de BMAD fait porter à ses workflows la mémoire et la fin
de tour du socle (F-0023@b8b44547). Une session réelle le confirme
(J-2026-10-19-K@a8e192bc), et montre la redondance : chaque outil a sa
façon de garder les décisions (les décisions d'architecture AD-n de BMAD,
les ADR), le travail prévu (l'état du sprint, le backlog), les travaux
reportés, le récit, et sa façon de consulter l'humain (l'arrêt dans la
conversation, la demande en file). Le même report s'y est écrit deux fois.
Théo a demandé un meilleur mariage et validé celui-ci
(J-2026-10-19-J@48b9451f).

## Décision

- **Planifier appartient à BMAD** : brief, PRD, architecture et ses
  décisions, epics, stories, specs, état du sprint, actions de
  rétrospective. Le socle ne les recopie pas, il les lit : son état au
  démarrage montre les specs non finies, les stories en cours ou en revue
  et les actions ouvertes ; ses contrôles jugent ces documents comme ceux
  du projet.
- **Prouver et retenir appartient au socle** : faits prouvés, consignes,
  décisions hors de l'architecture, journal, ce qui revient à l'humain, et
  le backlog des trouvailles. Un travail reporté par BMAD entre au backlog
  par une commande, et un contrôle refuse un report qui n'y est pas entré.
  Un travail fini laisse au journal une entrée qui cite sa spec, sans la
  recopier.
- **Une seule façon de consulter l'humain, un seul registre, deux
  formats.** En séance, BMAD demande dans la conversation (approuver une
  spec, trancher une question ouverte), et le socle consigne la question
  et la réponse mot pour mot dans le registre des demandes, sous une forme
  courte qui renvoie à l'artefact. En file, quand l'humain est absent ou
  que la décision doit survivre à la session, une demande complète. Une
  spec qui passe par l'approbation de BMAD ne quitte pas le brouillon sans
  une approbation consignée, et son intention figée ne change plus sans
  une approbation nouvelle.
- **Le lien passe par la personnalisation officielle de BMAD**, que
  l'installeur du socle pose quand BMAD est là : la mémoire en faits
  persistants, l'état à l'activation, la fin de tour du socle, et la
  consigne de laisser le bloc du socle d'AGENTS.md à son installeur. Aucun
  fichier de BMAD n'est modifié.
- Les décisions AD-n de BMAD lues comme une couche de décisions du socle
  (index, lecture prouvée) : plus tard, un sujet à part.

## Conséquences

Une seule liste par nature d'information, et un seul registre des
décisions de l'humain, que le socle contrôle. Le prix : le socle lit des
formats de BMAD (l'en-tête d'une spec, l'état du sprint, la liste des
reports), qui peuvent changer avec ses versions ; ses lecteurs restent
petits, tolérants, et éprouvés sur des fichiers réels de BMAD. Le
mécanisme ne s'active que si BMAD est présent ; sans lui, le socle est
inchangé. Pour défaire : retirer la personnalisation posée et les
lecteurs ; les deux outils cohabitent alors côte à côte, comme à l'essai.
