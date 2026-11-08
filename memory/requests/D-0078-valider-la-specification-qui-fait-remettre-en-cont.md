<!-- socle: couche=demandes zone=publique -->
# D-0078 — Valider la spécification qui fait remettre en contexte chaque demande : un contexte qui part du projet, et une relecture à froid avant de la poser (B-0130)

> date : 2026-11-08

## Décision demandée

Valider la règle proposée pour que chaque demande vous remette en
contexte, même après des semaines loin du projet : un contexte qui part du
projet et du but du travail, et une relecture à froid de la demande avant
de vous la poser.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie automatiquement ce que l'agent produit,
et vous pose sous forme de « demandes » les décisions qui vous reviennent.
Une demande est un fichier comme celui-ci : vous le lisez, et vous répondez
dans la conversation.

**Le chantier.** Vous essayez le socle sur un projet pilote, JustCook, et
vous me rapportez ce qui ne va pas ; je corrige le socle ici, et vous
fusionnez la pull request. Le but est de l'installer ensuite sur chess,
votre projet principal. Le plan que vous avez validé le 2 novembre
l'installe après deux journées de pilote sans retour qui oblige à corriger
le socle, puis une installation d'essai sur une copie de chess. Votre
retour du 8 novembre est un tel défaut : le compte repart de ce jour, et le
pilote continue pendant ce temps.

**La question.** Le 8 novembre, vous m'avez transmis une demande du pilote.
Elle portait sur les photos de tickets de caisse et de produits avec
lesquelles le pilote note des services d'IA de reconnaissance d'images, son
« banc d'essai ». Vous écriviez qu'elle ne remplit pas son rôle de mise en
contexte : « "le banc d'essai" => quel
banc d'essai ?? […] il faut rappeler ce qu'on fait, le but du truc etc ».
Vous demandiez s'il fallait un skill (une procédure écrite que l'agent
charge quand il en a besoin), un test, ou autre chose. Voici ma réponse. Elle change les règles de toute demande, d'où votre validation
avant que je l'écrive.

**Pourquoi cette demande a passé les contrôles.** Le socle vérifie qu'un
contexte fait au moins soixante mots et que chaque numéro cité, d'un sujet ou
d'une décision, est décrit en clair. La demande du pilote remplit les deux
conditions. Mais le gabarit des demandes, le modèle que le socle remplit
pour chaque demande nouvelle, demande « la tâche en cours, et ce qui a
déclenché la question », ce qui suppose le projet en tête. L'agent qui
écrit ne voit pas ce qui lui est implicite, et aucun test ne peut juger
si un texte se comprend seul : un lecteur, si.

**Une mesure.** J'ai fait lire cette demande à un sous-agent qui n'avait
que son texte, dans votre rôle : quelqu'un qui n'a pas ouvert le projet
depuis trois semaines. Il a écrit : « Le texte ne dit jamais ce que fait
l'application ». Il ne savait pas pourquoi on compare des fournisseurs
d'IA, il a relevé treize termes jamais expliqués, et il aurait répondu
`contexte-insuffisant`. Il a aussi réclamé des détails qui n'ont pas leur
place dans la demande, comme la liste des vingt-neuf produits, qu'une page
liée donne déjà : ses remarques se trient.

**La proposition, en deux parties.**
1. Le contexte de chaque demande commence par trois paragraphes, comme
   celui-ci : « Le projet » (ce qu'il fait, même si vous le savez), « Le
   chantier » (le but du travail en cours, ce qui est fait et ce qui
   reste, vos décisions passées dites par leur contenu et leur date) et
   « La question » (ce qui la pose maintenant). Tout terme propre au
   projet s'explique à sa première apparition. Le gabarit les porte, et
   le contrôle des demandes refuse une demande à laquelle il en manque
   un : il les reconnaît à leur nom en gras, comme ici. Que chaque terme
   soit expliqué, il ne peut pas le vérifier : c'est la seconde partie
   qui en juge.
2. Avant de vous poser une demande, l'agent la fait lire par un sous-agent
   qui n'a que son texte, dans votre rôle, comme ci-dessus ; une commande
   du socle imprime ce que le sous-agent reçoit. L'agent corrige ce que
   vous ne comprendriez pas davantage, et écarte, avec sa raison, ce qui
   n'aide pas à décider ou qu'un document lié donne déjà. Vous en voyez le
   bilan dans mon récap, le résumé qui clôt chacune de mes interventions.
   C'est votre « test » : le seul qui juge si un texte se comprend seul.
   Cette demande-ci y est passée : le relecteur a pu décider, et j'ai
   expliqué les termes qu'elle employait sans les définir.

La règle vaut pour toute demande, courte ou non, y compris les questions
ouvertes que je vous pose avant de spécifier un sujet ; pas pour une
décision que vous prenez en séance, que je transcris. Elle ne réécrit pas
les demandes déjà posées, celle du pilote comprise.

Ce qui reste hors de portée : le contrôle ne juge que la présence des
trois paragraphes, pas leur clarté, et rien ne prouve que la relecture a eu
lieu, sinon le récap, comme pour la revue du code avant chaque push.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision de conception, D-
une demande, J- une entrée du journal ; après @, l'empreinte de la version
que j'ai lue, une somme de contrôle de son texte.

- ADR-0046@56a1eda6 — la spécification proposée, à valider : ses deux
  parties, ce qu'elles changent, et ce qu'elles ne font pas.
- B-0130@5cad0686 — le sujet ouvert sur votre retour, et ses trois
  critères de fin : la spécification validée, le contexte vérifié par le
  contrôle, la relecture à froid écrite dans le skill `socle-request`.
- J-2026-11-08-A@4bd08673 — l'entrée du journal qui recopie votre message
  mot pour mot.
- D-0073@dca78105 — votre validation du 2 novembre du plan pour chess :
  deux journées de pilote sans défaut du socle, un essai à blanc, puis
  l'installation.
- ADR-0042@f52272e6 — la revue d'un lot de code par un sous-agent sans la
  conversation, que la relecture à froid imite.

## Où regarder

- [ADR-0046](https://github.com/theodubus/memory/blob/bedb64002e10343b4ab2c3ce5024a68b443c4088/memory/decisions/ADR-0046-une-demande-remet-en-contexte-l-humain-qui-revient.md) :
  la section « Décision ». À vérifier : que les trois paragraphes et la
  relecture répondent à votre retour, et que rien d'essentiel ne manque.
- [Le gabarit actuel des demandes](https://github.com/theodubus/memory/blob/bedb64002e10343b4ab2c3ce5024a68b443c4088/engine/socle/templates/request.md) :
  la ligne « La tâche en cours, et ce qui a déclenché la question », qui
  est à l'origine du défaut.
- [Votre message, au journal](https://github.com/theodubus/memory/blob/bedb64002e10343b4ab2c3ce5024a68b443c4088/memory/journal/2026-11.md#j-2026-11-08-a--retour-du-pilote--une-demande-ne-remet-pas-en-contexte-qui-revient-sur-le-projet-apr%C3%A8s-des-jours-d-0032-du-pilote) :
  le retour tel que vous l'avez écrit.

## Options

- **Les deux parties** (`valider`, recommandée) : effort nul pour vous ;
  chaque demande, qui fait déjà plusieurs centaines de mots, s'allonge
  d'une centaine et coûte une relecture, quelques centimes ; risque, des
  demandes plus longues ; réversible.
- **Les trois paragraphes seuls** (`structure`) : effort nul ; pas de
  relecture ; risque, le contrôle ne voit que la forme, et un paragraphe
  peut rester obscur sans que rien le signale ; réversible.
- **La relecture seule** (`relecture`) : effort nul ; le gabarit et le
  contrôle ne changent pas ; risque, rien n'oblige à partir du projet, la
  relecture le rattrape au cas par cas ; réversible.

## Conséquences

Si vous validez, j'écris le gabarit, le contrôle, la commande de la
relecture et l'étape du skill `socle-request`. La copie de ce skill dans
ce dépôt est protégée, elle ne change qu'avec votre accord : une seconde
demande, courte, vous en soumettra le texte, avec la consigne exacte du
relecteur, comme le 5 novembre pour le skill de la revue du code. Le pilote le reçoit
à sa mise à jour suivante. Si vous choisissez `structure` ou `relecture`,
je n'écris que cette partie. Si vous refusez, rien ne change, et je reviens
vers vous avec d'autres pistes. Sans réponse, rien ne s'écrit, et je
travaille sur autre chose.

## Recommandation

Valider les deux parties. Vérifié : la relecture à froid de la demande du
pilote a buté exactement là où vous avez buté, et le contrôle actuel ne
compte que des mots et des numéros décrits. Supposé : que trois paragraphes
imposés suffisent à cadrer, et que l'agent trie bien les remarques du
relecteur ; les premières demandes le montreront.

## Réponses possibles

- `valider` — les deux parties : les trois paragraphes et leur contrôle, puis la relecture à froid de chaque demande.
- `structure` — les trois paragraphes et leur contrôle seulement.
- `relecture` — la relecture à froid seulement.
- `refuser` — rien ne change ; l'agent revient avec d'autres pistes.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
