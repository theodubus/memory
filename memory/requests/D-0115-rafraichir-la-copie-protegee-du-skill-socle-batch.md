<!-- socle: couche=demandes zone=publique -->
# D-0115 — Rafraîchir la copie protégée du skill socle-batch depuis son gabarit : deux règles de la consommation, quand compacter et quel modèle

> date : 2026-11-15

## Décision demandée

Autoriser l'agent à remplacer la copie du skill `socle-batch` que lisent les sessions de ce dépôt, un fichier protégé, par le texte de son gabarit : deux points s'ajoutent à sa section « La consommation », rien d'autre ne change.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le moteur est ce qu'un projet reçoit à l'installation ; ce dépôt s'en sert lui-même, comme premier projet équipé.

**Le chantier.** Avant de construire les fonctions nouvelles du socle (la planification, puis la répartition du travail entre agents), l'agent finit une liste de corrections que vous avez fixée le 13 novembre. Il la livre par lots, des groupes de sujets du backlog (la liste des sujets à traiter, chacun nommé B-NNNN) livrés ensemble par une pull request qu'il fusionne lui-même. Le lot de ce jour finit le sujet de la consommation des limites d'usage de votre abonnement (une part par fenêtre de cinq heures, une par semaine, comptées en points de pourcentage), que vous avez rendu prioritaire le 12 novembre : chaque reprise après une coupure par la limite vidait la moitié de la fenêtre. Son dernier critère, une des conditions écrites qui disent le sujet fait : la méthode des lots dit quand compacter, combien de sous-agents à la fois, quand en reprendre un, quel modèle pour quel travail, et que faire près d'une limite. Les trois autres points y étaient déjà ; ce lot ajoute les deux qui manquaient.

**La question.** Un skill est une procédure écrite que l'agent charge quand il en a besoin ; `socle-batch` est celle qui mène un lot. Son gabarit, le texte de référence rangé dans le moteur, est ce que l'installeur (la commande qui pose ou met à jour les fichiers du socle dans un projet) recopie dans chaque projet ; la copie, dans `.claude/skills/`, est ce que lit une session de ce dépôt, et l'agent ne la modifie pas sans votre accord. Le gabarit a reçu les deux points ; la copie ne les a pas encore.

Les deux points, en entier, à la fin de la liste de « La consommation » :

> - L'agent ne compacte pas lui-même : il écrit la mémoire (chantier actif, journal), puis le demande à l'humain (sous Claude Code, `/compact`), à la fin d'un lot si l'humain garde la session au-delà, et avant toute attente qui peut passer l'heure sans changer de session (une CI longue, une réponse de l'humain, la nuit). Près d'une limite, le seuil plus haut prime : changer de session. Après la pause, il est trop tard : compacter relit alors toute la conversation au prix fort.
> - Le modèle : celui que demande la qualité du travail, jamais un moindre pour tenir une limite : une limite retarde un lot, elle ne l'allège pas. Entre ceux qui le font aussi bien, celui qui consomme le moins de la limite par jeton, surtout pour la conversation qui orchestre, relue à chaque appel ; l'humain choisit celui de la session, sur le conseil de l'agent. Celui que fixent les instructions du projet prime. Un sous-agent reçoit le sien explicitement à son lancement (outil `Agent` : `model`).

Les termes. « Compacter » : résumer la conversation de l'agent pour qu'elle coûte moins à chaque appel ; vous le lancez par la commande `/compact`, que l'agent ne peut pas lancer. « La mémoire », « le chantier actif », « le journal » : les fichiers du dépôt où l'agent écrit le travail en cours et ce qui s'est passé, que relit une session neuve ou compactée. « Passer l'heure », « au prix fort » : la conversation déjà lue reste en cache une heure ; au-delà, l'appel suivant la relit entière au plein tarif ; 39 points de la fenêtre de cinq heures ont été mesurés ainsi le 12 novembre, contre environ 8 pour un compactage fait avant la pause, l'appel suivant compris. « Le seuil plus haut » : le point précédent de la même section, qui fait changer de session au-delà de 85 % de la semaine ou de 60 % de la fenêtre de cinq heures. « Changer de session » : l'agent range la mémoire et vous donne le texte d'une session neuve, que vous ouvrez. « La conversation qui orchestre » : celle qui confie chaque sujet à un sous-agent, un agent auxiliaire lancé par l'outil `Agent`, dont le paramètre `model` fixe le modèle ; « en reprendre un » : lui renvoyer un message au lieu d'en lancer un neuf. « Par jeton » : le jeton est l'unité de texte que compte le modèle. « Les instructions du projet » : le fichier `AGENTS.md` et la mémoire ; ici, Opus partout depuis le 12 novembre.

D'où vient le texte. Une relecture adversariale du lot, par un sous-agent qui n'avait que le diff, a trouvé deux défauts dans la première rédaction : près d'une limite, elle proposait à la fois de compacter et de changer de session ; la règle du modèle pouvait se lire comme « le moins coûteux d'abord », et faire mener un long sujet sur un modèle moindre. Le premier est corrigé par « le seuil plus haut prime ». Sur le second, vous avez écrit aujourd'hui : « je ne veux pas que des lots soient bâclés pour correspondre aux limites » ; la règle dit maintenant la qualité d'abord, et la phrase « un plus coûteux seulement pour une tâche courte et bornée » en est sortie.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:96334d3e7e65e619

Les identifiants : B-NNNN, un sujet du backlog ; D-NNNN, une demande comme celle-ci ; J-AAAA-MM-JJ-X, une entrée du journal du jour, la lettre donnant son rang ; le suffixe après @, l'empreinte de la version lue.

- B-0173@43942422 — le sujet de la consommation : ses mesures des 11 et 12 novembre et ses critères, le dernier fait par ce lot.
- J-2026-11-15-C@76e14702 — l'entrée du journal qui consigne la relecture adversariale et les deux défauts corrigés.
- J-2026-11-15-D@28f58ce2 — l'entrée qui consigne votre message de ce jour, mot pour mot, et la règle du modèle récrite.
- D-0114@1535d227 — votre accord du 14 novembre, qui a posé la copie de ce skill nouveau à son texte actuel, `sha256:0a03e52f59883f1d`.
- B-0156@15e2df3a — le sujet du coût d'une conversation longue, où va le cas que ces règles laissent ouvert : vous êtes absent quand l'agent demande le compactage.

L'empreinte de la première ligne, les seize premiers caractères de l'empreinte SHA-256 du fichier, est celle que la copie aura après remplacement, identique à celle du gabarit : votre accord porte sur ce texte exact. Le contrôle des fichiers protégés, qui tourne à chaque commit, à chaque push et dans l'intégration continue sur GitHub, refuse une copie dont l'empreinte diffère de celle que cite votre validation.

## Où regarder

- [Le gabarit, le texte nouveau](https://github.com/theodubus/memory/blob/8f0e58477a90e3b2cd0617c03648d341c191a839/engine/socle/templates/skills/socle-batch/SKILL.md) : les deux points cités plus haut, à la fin de la section « La consommation ».
- [La copie actuelle, à remplacer](https://github.com/theodubus/memory/blob/8f0e58477a90e3b2cd0617c03648d341c191a839/.claude/skills/socle-batch/SKILL.md) : sans ces deux points, identique au gabarit pour le reste.
- [La pull request du lot](https://github.com/theodubus/memory/pull/54), que l'agent fusionne quand l'intégration continue passe : le gabarit part alors dans le moteur, quelle que soit votre réponse.
- [Le relevé de la consommation](https://github.com/theodubus/memory/blob/5760812c82f9a259b751729ea386ae04dc6ff0b1/docs/fabrication/consommation.md), section « Ce que la mesure suggère pour les règles », si vous voulez les chiffres.

Le gabarit existe aussi en anglais, pour les projets installés en anglais ; il a reçu les mêmes deux points. Ce dépôt est en français : seule la copie française est en jeu.

## Options

- Rafraîchir la copie : le gabarit recopié octet pour octet par l'installeur ; effort nul ; risque faible, une copie qui différerait du texte approuvé étant refusée par le contrôle ; réversible par une nouvelle demande qui reprend le texte d'avant.
- La laisser en retard : aucun effort ; une session qui mène un lot ici ne lit pas ces deux règles, peut laisser passer le moment de vous demander un compactage, au prix d'une relecture entière de sa conversation, et ne lit pas que le modèle se choisit pour la qualité.

## Conséquences

Si vous validez : l'agent recopie le gabarit dans la copie, et pousse votre réponse avec ce changement, dans le même push. Dès lors, dans ce dépôt, l'agent vous demandera `/compact` à la fin d'un lot si vous gardez la session, et avant une attente de plus d'une heure si vous ne changez pas de session ; il vous conseillera le modèle de la session s'il en voit un qui fait mieux le travail. Absent, vous ne compactez pas : la reprise coûte alors une relecture entière, ce que B-0156 cherche à éviter ; d'ici là, l'agent change de session à la fin du lot.

Si vous refusez : la copie garde son texte ; le gabarit reste celui que le moteur installe dans les autres projets, chess compris à sa mise à jour, et l'agent ouvre un sujet pour remettre les deux d'accord, dont le sens dépendra de la raison de votre refus, que vous pouvez dire dans la conversation. Sans réponse : rien ne change ici, et l'agent continue les lots suivants.

Valider fait appliquer ces deux règles aux sessions de ce dépôt ; ailleurs, elles s'appliquent avec le moteur, depuis la fusion. Les contester elles-mêmes se fait par un message dans la conversation, qui deviendra une décision nouvelle, et non par un refus de cette demande.

## Recommandation

Valider. Vérifié : la copie actuelle est octet pour octet le gabarit d'avant ce lot, celui de votre accord du 14 novembre (comparaison des deux fichiers) ; le gabarit ne diffère d'elle que par ces deux points (diff) ; l'empreinte citée est celle du gabarit ; les tests du skill, qui jugent les deux langues, leur plafond de 8 000 octets et l'absence de renvoi aux fichiers propres à ce dépôt, passent. Supposé : qu'une session qui lit la copie en retard manquerait le moment de compacter ; rien d'autre ne le lui rappelle.

## Réponses possibles

Répondez dans la conversation par l'un de ces mots ; l'agent consigne votre texte exact.

- `valider` — l'agent remplace la copie par le gabarit, et pousse votre réponse avec ce changement.
- `refuser` — la copie garde son texte actuel ; l'agent ouvre un sujet pour remettre la copie et le gabarit d'accord.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
