<!-- socle: couche=decisions zone=publique -->
# ADR-0046 — Une demande remet en contexte l'humain qui revient après des semaines : un contexte qui part du projet, et une relecture à froid avant de la poser

> statut : acceptée · date : 2026-11-08 · validation : D-0078@c7bdf1a6 · source : B-0130@5cad0686, J-2026-11-08-A@4bd08673 · lu : decisions@95c3299f

## Contexte

Une demande se lit quand le contexte est perdu : l'humain y revient
parfois après des jours ou des semaines. Le pilote en a posé une
(J-2026-11-08-A@4bd08673) qui remplit le contrat du socle, mais dont le
contexte commence par « Le banc d'essai note un fournisseur d'IA sur un
corpus annoté ». Elle ne dit ni ce que fait le projet, ni pourquoi un
banc, ni ce que l'humain a décidé avant. Le gabarit demande « la tâche en
cours, et ce qui a déclenché la question », ce qui suppose le projet en
tête, et le contrôle des demandes ne compte que des mots : soixante au
moins, et chaque identifiant décrit.

L'agent qui écrit ne voit pas ce qui lui est implicite, et aucun contrôle
mécanique ne juge si un texte se comprend seul. Un lecteur le peut. Le
8 novembre, un sous-agent qui n'avait que le texte de cette demande, dans
le rôle de l'humain qui revient après trois semaines, a écrit : « Le texte
ne dit jamais ce que fait l'application ». Il ne savait pas pourquoi on
compare des fournisseurs d'IA, il a relevé treize termes employés sans
explication, et il aurait répondu `contexte-insuffisant`. Il a aussi
demandé des détails qui n'ont pas leur place dans la demande, comme la
liste des vingt-neuf produits, qu'une page liée donne déjà.

La revue adversariale d'un lot (ADR-0042@f52272e6, ADR-0044@ea5c47f9)
procède de même : un sous-agent sans la conversation, un dossier que le
moteur imprime, et des constats que l'agent corrige ou écarte.

## Décision

**1. Le contexte part du projet.** La section « Contexte » d'une demande
commence par trois paragraphes, dans cet ordre, chacun ouvert par son nom
en gras :

- **Le projet.** Ce que fait le projet, et pour qui, en une ou deux
  phrases, même si l'humain le sait.
- **Le chantier.** Le but du travail en cours et pourquoi il existe, ce
  qui est fait et ce qui reste. Les décisions passées de l'humain qui y
  mènent se disent par leur contenu et leur date, pas par leur numéro.
- **La question.** Ce qui la pose maintenant.

Le détail suit, libre. Un terme propre au projet (« le banc », « le
corpus ») s'explique à sa première apparition. Le gabarit des demandes, en
deux langues (`**The project.**`, `**The work.**`, `**The question.**`),
porte ces trois paragraphes. Le contrôle des demandes refuse une demande à
laquelle il en manque un, ou dont l'un fait moins de quinze mots. La
règle vaut pour les demandes de décision et les questions de cadrage, pas
pour une décision prise en séance, qui transcrit la conversation. Une
demande posée avant le moteur qui l'apporte garde l'ancien contrat : elle
ne passe pas au rouge à la mise à jour.

**2. Une relecture à froid avant de poser la demande.** Avant de pousser
une demande, l'agent la fait lire par un sous-agent, du modèle de la
session, dont le seul message est le dossier de `socle review --request
D-NNNN` : une consigne, puis le texte de la demande, rien d'autre. La
consigne le met dans le rôle de l'humain qui n'a pas ouvert le projet
depuis trois semaines, lui interdit les liens et les fichiers, et lui
demande de rendre :
- le projet et le but du travail, en ses mots, tels que la demande les lui
  apprend ;
- la décision demandée, et ce que change chaque réponse ;
- chaque terme, nom ou renvoi employé sans explication ;
- ce qui lui manquerait pour décider sans chercher ailleurs.

L'agent compare ce que le lecteur a compris avec ce qu'il voulait dire, et
réécrit ce que l'humain ne comprendrait pas davantage. Il écarte, d'une
raison, ce qui n'a pas sa place dans la demande, comme un détail qu'un
document lié donne déjà. Son récap le dit : `Relecture à froid : <n>
points, <k> corrigés ; écartés : …`. Le skill `socle-request` gagne cette
étape ; un agent sans sous-agents la saute, et son récap le dit.

**3. Ce qui n'est pas fait.** Aucun contrôle ne juge la qualité du
contexte : il ne vérifie que sa forme. Aucun ne prouve que la relecture a
eu lieu : comme la revue d'un lot, c'est une procédure, dont la trace est
le récap. Les instructions posées dans un projet (`AGENTS.md`) ne changent
pas : le skill porte la procédure, et la section du socle n'y grossit
pas.

## Conséquences

L'humain qui revient sur un projet retrouve, en tête de chaque demande,
ce que fait le projet et où en est le chantier. Une demande coûte une
relecture de plus, quelques centimes, sur l'abonnement du projet. Le skill
`socle-request`, protégé, change : dans ce dépôt, sa copie se valide par
une demande, comme celle de `socle-review` (D-0074@a5cc393b). Se défait en retirant
les trois paragraphes du gabarit et du contrôle, et l'étape du skill.
