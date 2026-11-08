<!-- socle: couche=demandes zone=publique -->
# D-0080 — Valider la règle de la reprise après une limite d'usage, écrite ici en entier : deux réveils pendant chaque tour de travail, qui ne relancent qu'un agent coupé (B-0132)

> date : 2026-11-08

## Décision demandée

Valider la règle ci-dessous, qui fait reprendre seul un agent coupé par une
limite d'usage dès qu'elle se lève, sans relancer un agent que rien n'a
coupé, que vous avez arrêté, ou dont le travail a repris ailleurs.
Répondez dans la conversation par l'un des mots de la fin ; une condition
que vous y ajoutez sera recopiée mot pour mot.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
sous forme de « demandes », des fichiers comme celui-ci, les décisions qui
vous reviennent. Son but est que l'agent travaille en autonomie.

**Le chantier.** L'agent travaille dans une session cloud de Claude Code :
une session qui tourne sur un serveur, et que vous suivez depuis
l'application ou le navigateur. Une limite d'usage de votre compte peut la
couper, sur une fenêtre de cinq heures ou sur une de sept jours ; coupé,
l'agent ne reprend qu'à votre message suivant. Le soir du 8 novembre, vous
avez refusé le rappel que je proposais, toutes les deux heures de 8 h à
22 h, et posé six exigences, recopiées plus bas avec ce qui y répond. Trois
versions de cette règle, relues chacune par un agent qui n'avait que leur
texte, avaient des trous : elles sont abandonnées. Celle-ci est écrite ici
en entier.

**La question.** Faut-il adopter cette règle ? Elle s'appliquera à tout
projet équipé du socle, d'où votre validation avant que je l'écrive.

**Ce que l'agent voit**, relevé le 8 novembre, heures de Paris. La session
enregistre ses événements : à chaque appel au modèle, le remplissage des
deux fenêtres et l'heure de leur remise à zéro ; pour chaque tour (ce que
fait l'agent entre deux messages reçus), sa fin : normale, interrompue par
vous, ou arrêtée sur une limite, en cours de route (coupée) ou d'emblée
(refusée). À 13 h 32, la fenêtre de cinq heures était à 99 %. À 14 h 14, un
rappel que je m'étais programmé pour surveiller une pull request a ouvert
un tour, refusé ; rien ne l'a relancé. La fenêtre s'est remise à zéro à
16 h 50 ; je n'ai repris qu'à votre message, à 17 h 45. Un tour refusé ne
fait rien.

**Les mots.** Un rappel : un message que l'agent programme pour sa propre
session, à une heure donnée ; il figure dans la liste des tâches
programmées de votre compte. Un réveil : un rappel armé pour reprendre
après une coupure, que l'agent déplace ou retire. Un lot : les sujets que
l'agent annonce puis traite d'affilée ; une étape, une partie d'un lot,
comme écrire le code ou le faire relire. Un sous-agent : un second agent
lancé pour une tâche à part, dont l'agent attend le résultat. Une branche :
la copie de travail où l'agent commite. L'installeur : la commande du socle
qui équipe un projet ou le met à jour. Le pilote : le premier projet réel
équipé du socle.

**La règle.**
1. *Armer.* Au début de chaque tour où il agit (une commande, un fichier,
   un sous-agent ; pas une réponse en texte seul), l'agent arme deux
   réveils, de jour comme de nuit et quel que soit le remplissage : cinq
   minutes après la remise à zéro de la fenêtre de cinq heures, et cinq
   après celle de la semaine, une marge contre un écart d'horloge. S'ils
   existent, il les déplace, sans en ajouter.
2. *Tenir à jour.* À chaque étape, et à chaque sous-agent lancé ou rendu,
   il récrit le texte des réveils, où il retrouvera, au réveil : le lot,
   l'étape, chaque sous-agent en cours et ce qu'il doit rendre. Il recale
   aussi leur heure si une fenêtre s'est remise à zéro pendant le tour.
3. *Retirer.* À la fin de chaque tour, il retire ses réveils, sauf si un
   sous-agent tourne encore : ils restent alors jusqu'au tour qui reçoit
   son résultat. Un tour coupé ou refusé ne retire rien : celui de la
   semaine survit au tour refusé qu'ouvre celui de cinq heures pendant une
   coupure de la semaine.
4. *Au réveil, vérifier d'abord.* Le tour d'avant est le dernier avant ce
   réveil, quoi qui l'ait ouvert : votre message, le résultat d'un
   sous-agent, un autre réveil. L'agent lit dans les événements comment il
   a fini, et tous les messages arrivés depuis la coupure, même refusés. Il
   ne reprend pas si ce tour n'a pas fini sur une limite (vous l'avez
   interrompu, par exemple) ; si vous avez écrit pendant la coupure, et il
   répond alors à votre message ; si une autre session a poussé sur sa
   branche depuis son dernier commit ; si sa pull request a été fusionnée
   ou fermée depuis. Il répond alors en une ligne et retire ses réveils,
   ou les recale si un sous-agent tourne encore. Sinon, il reprend l'étape
   notée, relance chaque sous-agent dont le résultat n'est pas arrivé, et
   continue comme si vous aviez écrit « reprends ».
5. *Où elle vit.* Un skill du socle, `socle-reprise` : une procédure écrite
   que l'agent charge quand il en a besoin, que l'installeur pose dans tout
   projet. Le moteur du socle, le programme qui fait les contrôles, n'en
   sait rien, et aucun contrôle ne prouve que l'agent l'applique. Hors
   d'une session cloud de Claude Code, le skill est inerte : l'outil qui
   programme un rappel n'y existe pas.

**Vos six exigences, une par une.**
- « Ça serait hors socle que tu mettrais ça en place ? » — Non : un skill
  du socle, posé partout (point 5).
- « l'agent se prend des rappels pendant qu'il n'est pas coupé » —
  Satisfaite, sauf trois cas rares d'un tour d'une ligne, dits plus bas :
  les réveils se retirent à chaque fin de tour (point 3).
- « Je ne sais pas si ta solution gère les sous agents coupés » — Oui : un
  sous-agent coupé fait refuser le tour qui devait recevoir son résultat,
  et le réveil, qui le nomme, le relance (points 2 à 4).
- « Pourquoi ne pas mettre de rappels la nuit ? » — Satisfaite : l'heure
  de la remise à zéro, quelle qu'elle soit (point 1).
- « Il ne faut pas que la solution mise en place reveille des sessions
  mortes » — En partie : seul un tour coupé laisse des réveils, qui ne
  tombent qu'une fois, au plus sept jours après. Une session coupée puis
  laissée par vous reprend donc une fois son travail, sauf si vous y avez
  écrit « arrête », à tout moment.
- « Impossible pour l'agent de voir les credits de session ou weekly
  restants ? » — Il les voit (plus haut) ; la règle n'en prend que l'heure
  de la remise à zéro.

**Ce qu'elle laisse passer.** Trois cas ouvrent un tour d'une ligne : un
tour que vous interrompez sans réécrire avant la remise à zéro ; une étape
longue pendant laquelle tombe l'heure d'un réveil, qui attend la fin du
tour ; un réveil qui tombe pendant qu'un sous-agent tourne encore, le tour
fini. Plusieurs sessions coupées ensemble reprennent ensemble, et partagent
la fenêtre neuve. Une session que vous ouvrez ailleurs sans y avoir rien
poussé, l'agent ne la voit pas : les deux travailleraient en même temps.
Une session archivée (close dans l'application) : je n'ai pas mesuré si
ses réveils y tombent encore ; ils se suppriment dans la liste des tâches
programmées, sous le nom « Reprise après limite » suivi du projet.

**Ce qui reste supposé.** Qu'un réveil, cinq minutes après la remise à
zéro, trouve la limite levée et reprenne la session : la première coupure
réelle le dira, comme elle dira si un sous-agent coupé fait bien refuser
le tour qui attend son résultat. Sinon, je vous propose par une demande de
corriger le skill ou de le retirer.

**Le coût.** Une dizaine d'appels d'outil par tour de travail : armer,
récrire à chaque étape, retirer. Chacun prend une petite part de la
fenêtre, comme tout appel ; un tour de travail en fait des dizaines.

**La portée.** Ce dépôt se sert lui-même du socle ; sa copie du skill est
protégée, et ne change que par une demande qui vous en montre le texte
exact : il l'appliquera dès cette seconde demande validée. Les autres
projets équipés, comme le pilote, le reçoivent à leur mise à jour du
socle, que leur humain approuve. Le retirer : une demande ; un projet déjà
équipé garde sa copie jusqu'à ce que son humain la retire.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision de conception, J-
une entrée du journal ; après @, l'empreinte de la version que j'ai lue,
une somme de contrôle de son texte.

- B-0132@cc8d5405 — le sujet ouvert sur votre demande ; il est fait quand
  la règle est validée, posée dans tout projet, et qu'une coupure réelle a
  repris sans votre message.
- J-2026-11-08-H@3d8256b3 — votre message du 8 novembre, mot pour mot.
- J-2026-11-08-I@4e3666a8 — la coupure du 8 novembre, heure par heure.
- J-2026-11-08-J@ef61624c — pourquoi la règle est écrite ici en entier.
- ADR-0047@6c9bbf4f, ADR-0048@daa1288e et ADR-0049@4aa3a77e — les trois
  versions abandonnées, chacune sur un trou que sa relecture a trouvé.

## Où regarder

- [La coupure du 8 novembre, au journal](https://github.com/theodubus/memory/blob/1507b4bff3c3e39e13857966590e60300a761e8e/memory/journal/2026-11.md#j-2026-11-08-i--ce-que-la-session-garde-dune-coupure-par-limite--lavertissement-%C3%A0-90--le-refus-et-sa-cause-lheure-de-la-remise-%C3%A0-z%C3%A9ro) : ce que la session en garde, si vous voulez le vérifier.

## Options

- **La règle** (`valider`, recommandée) : effort nul pour vous ; une
  dizaine d'appels d'outil par tour ; risque, qu'un réveil ne reprenne pas
  une session coupée, ce que la première coupure dira ; réversible, par
  une demande.
- **Refuser** (`refuser`) : effort nul ; vous relancez l'agent après chaque
  coupure, comme aujourd'hui ; réversible.

## Conséquences

Si vous validez, j'écris une décision de conception qui recopie cette
règle, puis le skill `socle-reprise`, en français et en anglais, les deux
langues où le socle s'installe ; une seconde demande, courte, vous soumet
sa copie dans ce dépôt. Si vous refusez, rien ne change, et je reviens
vers vous avec d'autres pistes. Sans réponse, rien ne s'écrit, et je
travaille sur autre chose.

## Recommandation

Valider. Vérifié : la session donne le remplissage des deux fenêtres,
l'heure de leur remise à zéro et la fin de chaque tour ; un rappel tombé
pendant la limite a ouvert un tour refusé, que rien n'a relancé. Supposé :
qu'un réveil tombé après la remise à zéro reprenne la session.

## Réponses possibles

- `valider` — l'agent écrit la règle en décision de conception, puis le skill `socle-reprise`.
- `refuser` — rien ne change ; l'agent revient avec d'autres pistes.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
