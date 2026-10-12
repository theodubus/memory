<!-- socle: couche=demandes zone=publique -->
# D-0017 — Passer le backlog à un fichier par sujet, dans un dossier

> date : 2026-10-12 · lu : decisions@8e6f1b5f

## Décision demandée

Passer le backlog d'un fichier unique à un fichier par sujet, dans un
dossier, comme les décisions et les demandes ; et, si oui, quand.

## Contexte

Tu as demandé : « est ce que ça serait bien de séparer la backlog en
plusieurs fichiers dans un dossier comme les arbitrages ? Ça permettrait
aussi mieux de les détailler et d'en choisir à privatiser au détail ».
Aujourd'hui, le backlog est un seul fichier, comme le veut la décision qui
fixe l'arborescence de la mémoire, que tu as validée le 10 octobre : un
fichier par couche durable, un fichier par décision et par demande. Il fait
22,6 Ko pour un plafond de 24 Ko, avec 35 sujets : détailler un sujet
pousse déjà contre le plafond, et les sujets clos partent au journal pour
faire de la place. Privatiser au détail existe déjà : un sujet neuf peut
être écrit dans le backlog privé, et un sujet public existant basculer en
privé ; avec un fichier par sujet, ce serait un simple déplacement. Changer
la forme du backlog change le format d'un projet installé : il faut une
migration scriptée, comme celle des noms anglais. Le sujet des noms encore
en français demandera lui aussi une migration ; les faire ensemble en
épargne une aux projets.

## Éléments cités

- **La décision sur l'arborescence de la mémoire** (ADR-0003@a701a157) : un
  fichier par couche durable, dont le backlog ; un fichier par mois de
  journal, par décision et par demande. La changer après des installations
  exige une migration.
- **Le sujet des noms encore en français** (B-0045@d35a99b1) : des
  dossiers, gabarits et commandes à renommer, avec une migration pour ce
  qui vit dans les projets.
- **Le backlog de ce dépôt**, mesuré aujourd'hui : 22 646 octets pour un
  plafond de 24 000, 35 sujets ouverts ou en cours.
- **Ce que le changement toucherait** : la lecture de la mémoire, la
  commande qui crée un sujet, l'index du backlog et son empreinte (la
  preuve de lecture), l'archivage des sujets clos (inutile avec un fichier
  par sujet), la bascule en privé, les plafonds de taille, la
  spécification du format, les gabarits, les tests et l'auto-test.

## Où regarder

- [le backlog](https://github.com/theodubus/memory/blob/6d56ee6298135587a06aa0d90e28c584f3c8627a/memory/backlog.md) :
  sa taille, et la place que prend chaque sujet détaillé.
- [la décision sur l'arborescence](https://github.com/theodubus/memory/blob/6d56ee6298135587a06aa0d90e28c584f3c8627a/memory/decisions/ADR-0003-arborescence-et-format-de-la-memoire.md) :
  ce qu'elle fixe, et ce qu'elle dit d'un changement après installation.
- [le sujet des noms en français](https://github.com/theodubus/memory/blob/6d56ee6298135587a06aa0d90e28c584f3c8627a/memory/backlog.md#b-0045--des-noms-de-fichiers-et-de-dossiers-sont-encore-en-fran%C3%A7ais) :
  vérifier qu'une seule migration peut porter les deux.
- [la spécification du format](https://github.com/theodubus/memory/blob/6d56ee6298135587a06aa0d90e28c584f3c8627a/moteur/socle/FORMAT.md) :
  la couche backlog, l'archivage des sujets clos et la preuve de lecture,
  qui changeraient.

## Options

- **Oui, avec les noms anglais, dans une seule migration**, après les lots
  de la passe de recul et R6, avant la documentation à refaire : un
  fichier par sujet dans un dossier backlog de la mémoire, son pendant
  dans la zone privée, plus d'archivage au journal, un plafond par
  sujet. Effort moyen à important, un lot entier ; risque : une migration
  de format (éprouvée sur la copie du projet d'échecs de R6, installée
  d'ici là) ; réversible par une migration inverse.
- **Oui, tout de suite**, avant L5 : effort identique ; repousse les lots
  restants et la mesure de R6, et ferait deux migrations au lieu d'une.
- **Non, un fichier unique**, avec un plafond relevé ou un archivage plus
  tôt des sujets clos : effort faible ; ne règle ni le détail ni le
  privé au sujet près, au-delà de ce qui existe.

## Conséquences

- Si tu valides : j'écris la décision qui remplace l'arborescence pour le
  backlog, et je fais le lot avec les noms anglais, à la place prévue.
- Si tu choisis tout de suite : je le fais avant L5.
- Si tu refuses : le backlog reste un fichier ; je ne touche qu'au plafond
  si tu le demandes.
- Sans réponse : rien ne change ; la question reste au backlog.

## Recommandation

Oui, avec les noms anglais, dans une seule migration, après les lots en
cours : un sujet détaillé n'aurait plus de plafond commun, un sujet
privatisé ne serait qu'un fichier déplacé, deux sessions en parallèle ne
se disputeraient plus le même fichier, et la documentation à refaire
décrirait la forme finale. Vérifié : la taille et le nombre de sujets du
backlog ; les décisions et les demandes sont déjà un fichier chacune, et
leur lecture sert de modèle ; la bascule en privé existe déjà au sujet
près. Supposé : l'effort, estimé sans l'avoir fait, et qu'aucun projet
installé hors de la copie de R6 n'aura à migrer d'ici là.

## Réponses possibles

- `valider` — un fichier par sujet, avec les noms anglais, dans une seule migration, après les lots en cours.
- `maintenant` — un fichier par sujet tout de suite, avant L5.
- `refuser` — le backlog reste un fichier unique.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
