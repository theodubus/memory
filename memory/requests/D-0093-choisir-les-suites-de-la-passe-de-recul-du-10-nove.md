<!-- socle: couche=demandes zone=publique -->
# D-0093 — Choisir les suites de la passe de recul du 10 novembre, et les jalons de ce dépôt

> date : 2026-11-10

## Décision demandée

Valider les sept propositions de la passe de recul et les quatre jalons qui
les ordonnent, ou dire lesquelles écarter et quel ordre changer.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA : il tient la mémoire
du projet, et des contrôles automatiques vérifient ce que l'agent produit.
Il sert aujourd'hui sur ce dépôt et sur JustCook, votre application de
cuisine, le projet pilote. chess, votre moteur d'échecs, le projet d'où le
socle vient, ne l'a pas encore reçu.

**Le chantier.** Le cadrage, le document fondateur du 10 octobre, visait
six problèmes d'un projet entretenu par un agent : la reprise sans
contexte, la documentation périmée, les tests qui ne prouvent rien, les
affirmations inventées, la mémoire qui grossit sans borne, les décisions
demandées sans contexte. Ses neuf étapes sont livrées. Depuis fin octobre,
le travail suit surtout les retours du pilote : ce 10 novembre, JustCook a
reçu la dernière version et rapporté six gênes, dont trois sont corrigées.
Le matin, vous aviez accepté que je vous propose des jalons : un jalon est
un sujet du backlog (la liste des travaux) qui regroupe des tâches et dit
l'objectif suivant.

**La question.** Ce 10 novembre, vous avez écrit : « fais une passe ou tu
prends du recul, tu regarde tout le projet a quoi il sert et a quoi il est
censé servir (code, doc, etc), et (s'il y a lieu d'être) fais des
propositions ». La passe est faite. Ses propositions changent l'ordre du
travail, et deux d'entre elles touchent à ce que vous avez décidé : elles
vous reviennent.

### Ce que la passe constate

1. **Le périmètre a glissé.** Le cadrage écartait le suivi de tâches et
   l'organisation du travail. Le socle ordonne aujourd'hui le backlog,
   règle la livraison et sa relecture par un second agent, relance l'agent
   quand la limite de consommation de votre abonnement l'a coupé. Chaque
   ajout répondait à un besoin, surtout après le retrait de BMAD, une
   méthode de planification tierce essayée en octobre. Le socle est devenu
   deux choses : un noyau qui fiabilise, une méthode qui organise.
2. **Le coût pour l'agent a monté.** Le code du socle a doublé en un mois,
   à 18 000 lignes. À chaque début de session, l'agent reçoit ici 26,6 Ko
   de mémoire à lire, quand le cadrage voulait un démarrage léger. Un
   correctif d'une ligne demande plus de vingt opérations : note au
   journal, sujet, relecture, compte rendu.
3. **Le coût pour vous aussi.** Quatre-vingt-douze demandes en cinq
   semaines, dont soixante-sept à lire (les autres consignent une décision
   prise en conversation), alors que le cadrage voulait limiter vos
   validations.
4. **La valeur n'est pas mesurée en usage réel.** Les essais du socle
   mesurent des fautes injectées exprès. Sur le pilote, rien ne compte les
   fois où un contrôle a bloqué l'agent à raison, et celles où il l'a
   bloqué à tort. Un blocage à tort de ce 10 novembre : mon compte rendu
   refusé parce qu'un mot entre accents graves n'était pas un nom de
   fichier.
5. **chess recule.** Le plan que vous avez validé le 2 novembre attend,
   avant chess, deux journées de travail du pilote sans retour qui corrige
   le socle, pour ne pas y installer un outil encore instable. Chaque
   nouvelle version apporte de tels retours : six ce 10 novembre, dont un
   seul grave, l'état du projet devenu illisible. Tant que le socle change
   à ce rythme, la condition ne se remplit pas.
6. **La documentation de fabrication grossit.** Le document
   d'architecture, qui dit ce que fait chaque fichier du code, pèse
   41,7 Ko : chaque correctif y ajoute une phrase, parce qu'un contrôle
   exige que la documentation change avec le code.
7. **Vos consignes durables n'ont pas de place.** « Les heures à l'heure
   de Paris », par exemple, vit dans le chantier actif, le fichier du
   travail en cours, plein à 98 % de sa taille permise.
8. **Les conversations trop longues coûtent.** Une session neuve repart
   de la mémoire pour presque rien ; une conversation longue se relit à
   chaque opération. Celle du 10 novembre a été coupée par la limite de
   votre abonnement.

### Les sept propositions

L'effort se compte en sessions de travail de l'agent.

1. **Alléger le début de session**, sous 10 Ko : les dix dernières
   décisions du projet au lieu des cinquante-six, les faits établis par
   leur titre ; le reste se lit à la demande, comme le backlog
   aujourd'hui. Les rappels qui relancent l'agent après une coupure
   s'écrivent une fois par intervention, au lieu de chaque opération. Si
   les essais de reprise du socle échouent ensuite, on revient en arrière.
   Une session.
2. **Une session par lot.** Quand la conversation dépasse une taille à
   fixer, le compte rendu propose de continuer dans une session neuve.
   Moins d'une session.
3. **Une place pour vos consignes** dans la mémoire, remise à l'agent au
   début de session, chacune en vigueur ou levée. Deux sessions.
4. **Une architecture courte** : un paragraphe par fichier du code ;
   l'historique des correctifs en sort, les décisions et le journal le
   gardent déjà. Le contrôle reste. Une session.
5. **chess, prochain objectif.** Jusqu'à son installation, le socle ne
   reçoit que des correctifs : rien de nouveau qu'il exige de l'agent ou
   lui refuse. La condition du 2 novembre devient « deux journées du
   pilote sans retour bloquant » : bloquant, un retour qui arrête l'agent
   du pilote ou fausse un contrôle ; une gêne qui se contourne va au
   backlog sans remettre le compte à zéro. Vous en jugez, sur le retour du
   pilote. Ce que vous lâchez : chess recevra un socle qui a encore de
   petites gênes connues.
6. **Mesurer en usage réel.** Une commande qui ne fait que lire relève
   les blocages par contrôle et les demandes par semaine ; un relevé
   mensuel dit quels contrôles gardent leur place. Aucune proposition ne
   réduit d'elle-même vos demandes ni les opérations d'un petit
   correctif : celle-ci les mesure d'abord. Une session.
7. **Séparer le noyau de la méthode.** La méthode (livraison par lots,
   relecture, reprise, planification) deviendrait un ensemble de pièces
   que chaque projet choisit. Coûteux à défaire : aujourd'hui, je vous
   demande seulement de pouvoir vous poser des questions de cadrage, après
   chess. Rien ne change pour JustCook d'ici là.

Deux sujets du backlog en dépendent. La procédure de planification par
l'agent, à écrire, que vous aviez débloquée ce matin, est une pièce de la
méthode : elle attendrait chess et la proposition 7. Le mode à plusieurs
agents, à écrire aussi, que le cadrage écartait, serait abandonné.

### Les jalons proposés

- **Jalon 1, « Alléger »**, deux à trois sessions : les trois sujets déjà
  annoncés (deux pour la prochaine mise à jour de JustCook, un de sûreté),
  puis les propositions 1 et 2.
- **Jalon 2, « chess équipé »** : la proposition 5. Pendant les deux
  journées du pilote : la proposition 4 et les correctifs ouverts, une
  dizaine. Puis l'essai à blanc et l'installation, deux sessions.
- **Jalon 3, « Mesurer »** : la proposition 6, en parallèle du jalon 2.
- **Jalon 4, « Le noyau et la méthode »**, après chess : les propositions
  3 et 7, qui ajoutent des règles.

L'ordre inverse, chess avant d'alléger, gagnerait deux à trois sessions
sur chess ; il y installerait le début de session lourd d'aujourd'hui.

## Éléments cités

Les numéros : B- un sujet du backlog, D- une demande comme celle-ci ;
après @, l'empreinte de la version que j'ai lue.

- D-0073@f690f8a8 — votre décision du 2 novembre : le plan pour chess,
  dont la condition des deux journées sans retour qui corrige le socle.
- B-0126@e4f0cc19 — le sujet de l'installation du socle sur chess.
- B-0010@98572a02 — le sujet, ouvert en octobre, du calibrage de ce que
  l'agent reçoit au début de session ; la proposition 1 le reprend.
- B-0101@cdd9ca34 — le sujet de la planification par l'agent.
- B-0055@43000c48 — le sujet du mode à plusieurs agents.
- D-0090@e262f304 — votre accord du 10 novembre pour que je vous propose
  des jalons, et pour lancer la planification sans attendre.
- B-0149@8bca99c5, B-0151@783a3fab — les deux sujets de la prochaine mise
  à jour de JustCook : la taille d'une demande de mise à jour, les notes
  de version.
- B-0141@3011073d — le sujet de sûreté : le second agent qui relit un lot
  peut agir dans le dépôt.

## Où regarder

- [Le relevé de la passe](https://github.com/theodubus/memory/blob/69fbbb175515c1cffd7effcc9f62a95a87665651/docs/fabrication/recul.md#la-passe-du-10-novembre-2026) :
  le tableau des chiffres mesurés, que cette demande ne reprend qu'en
  partie ; les constats et les propositions y sont les mêmes, en plus
  court. Vérifier que les constats correspondent à ce que vous voyez du
  projet.

## Options

- **Valider** : aucun effort pour vous. Les quatre jalons s'ouvrent au
  backlog, dans cet ordre. Votre texte peut écarter une proposition ou
  changer l'ordre : « valider, sauf la 7 », « valider, chess d'abord ». Ce
  que valider engage : l'ordre du travail, la nouvelle condition de chess
  (proposition 5) et l'abandon du mode à plusieurs agents. Les
  propositions 3 et 7 vous reviendront chacune par une demande avant tout
  code ; les autres sont des choix réversibles, que j'écris en décisions
  du projet. Réversible : un jalon se réordonne ou s'abandonne.
- **Refuser** : aucun effort. Aucun jalon ; après les trois sujets en
  tête, le travail continue sur les correctifs ouverts, par ordre de gêne.
  Risque : les coûts constatés restent, et chess attend.

## Conséquences

Si vous validez, j'ouvre les jalons et leurs sujets au backlog, et
j'écris la décision qui remplace la condition de chess. Si vous refusez,
rien ne s'ouvre. Sans réponse, je traite les trois sujets en tête du
jalon 1, qui ne dépendent pas de ces choix ; votre réponse compte à leur
fin.

## Recommandation

Valider, dans cet ordre : alléger d'abord, brièvement, parce que cela
baisse le coût de tout le reste, chess compris. Vérifié : les chiffres
cités, mesurés ce 10 novembre sur ce dépôt. Supposé : qu'un début de
session de 10 Ko suffise à l'agent ; que n'ajouter aucune règle suffise à
remplir la condition de chess ; les efforts annoncés.

## Réponses possibles

- `valider` — les sept propositions et les quatre jalons, dans l'ordre recommandé ; votre texte peut en écarter ou changer l'ordre.
- `refuser` — aucun jalon ; le travail continue sur les sujets annoncés, puis les correctifs ouverts.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
