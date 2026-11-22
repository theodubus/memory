<!-- socle: couche=decisions zone=publique -->
# ADR-0106 — La mesure de la consommation lit les transcriptions de Claude Code dans le moteur, comme le hook de fin de tour : une commande du produit, son format lu en un seul endroit

> statut : acceptée · date : 2026-11-22 · source : B-0201@07c63c6b, T-0033@5a1d0dac, ADR-0007@d1b9c2e7, ADR-0033@44523582, ADR-0001@692e0dfc · lu : decisions@2f9746c5

## Contexte

B-0201@07c63c6b fait entrer dans le produit l'outil de l'atelier qui dit
ce qu'une session a coûté et ce qui l'a fait coûter. Il lit les
transcriptions de Claude Code : un format d'un agent, quand la règle du
dépôt veut que le moteur ne connaisse ni langage ni agent, le langage
dans un adaptateur, l'agent dans les hooks. Le moteur lit déjà un
transcript de Claude Code : le hook de fin de tour y cherche le dernier
message de l'agent (`human.dernier_message`, ADR-0007@d1b9c2e7), et
l'ADR en accepte la dépendance au format. Mais c'était un hook, qui
reçoit de Claude Code le chemin du transcript ; une commande que
l'humain lance doit trouver seule le dossier des transcriptions, et
c'est la première commande du produit qui ne vaut que sous un seul
agent.

## Décision

1. La mesure est une commande du produit, `socle consumption`, dans le
   module `consumption.py` du moteur, en bibliothèque standard seule
   (ADR-0001@692e0dfc), rangée dans l'aide avec les commandes de
   l'humain : c'est lui qui veut savoir ce qu'une session a coûté.
2. Comme pour le hook de fin de tour, le format de Claude Code se lit
   dans le moteur, et en un seul endroit : trois fonctions de lecture
   (`dossier_de_claude_code`, `lire_dossier`, `lire_conversation`). Le
   reste du module ne connaît que des appels, des compactages, des refus
   d'usage et ce que le socle a injecté : un autre agent s'y brancherait
   par une autre lecture, sans toucher au calcul. Pas d'adaptateur
   d'agent pour un seul lecteur.
3. Sans argument, la commande lit le dossier que Claude Code tient pour
   le projet : sous `CLAUDE_CONFIG_DIR`, sinon `~/.claude`, `projects/`
   puis le chemin absolu du projet, chaque signe qui n'est ni lettre ni
   chiffre changé en tiret ; un autre dossier se donne en argument. Sous
   un autre agent, ou quand la règle de nommage change, elle dit qu'elle
   ne trouve aucune transcription, et rend 1, sans rien deviner.
4. Le produit ne renvoie pas à l'atelier (ADR-0033@44523582) : le
   module, ses messages, le guide et la note de version ne citent ni la
   mémoire de ce dépôt, ni son banc, ni son relevé ; l'outil de l'atelier
   disparaît, ses tests deviennent ceux du module, et le relevé de
   l'atelier cite la commande. Les messages passent par le catalogue,
   les nombres prennent la décimale de la langue du projet.

## Conséquences

- Un projet équipé sait d'une commande ce qu'une session a coûté, sans
  installer ni chercher l'outil.
- Le moteur dépend un peu plus du format de Claude Code : un changement
  de ce format casse la lecture, pas le reste du moteur, et la commande
  le dit par un rapport vide ou un dossier introuvable ; les tests du
  module fabriquent leurs transcriptions, et ne voient donc pas un tel
  changement.
- Se défait sans coût pour un projet : retirer la commande et son module,
  personne d'autre ne les appelle.
