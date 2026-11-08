<!-- socle: couche=decisions zone=publique -->
# ADR-0050 — Un agent coupé par une limite d'usage reprend seul : deux réveils pendant chaque tour de travail, qui ne relancent qu'un agent coupé

> statut : acceptée · date : 2026-11-08 · validation : D-0080@bf2d22c6 · source : B-0132@cc8d5405, J-2026-11-08-K@80140e4f · lu : decisions@847dd645

## Contexte

Une session cloud de Claude Code que coupe une limite d'usage, sur cinq
heures ou sur sept jours, ne reprend qu'au message suivant de l'humain.
Théo veut qu'elle reprenne seule, dans le socle, sans relancer un agent
que rien n'a coupé, en reprenant les sous-agents coupés, de jour comme de
nuit, sans réveiller une session morte (J-2026-11-08-H@3d8256b3). La session
enregistre le remplissage des deux fenêtres, l'heure de leur remise à
zéro et la fin de chaque tour (J-2026-11-08-I@4e3666a8). Trois versions écrites en
décisions avant d'être relues ont été abandonnées sur leur relecture à
froid (ADR-0047@6c9bbf4f, ADR-0048@daa1288e, ADR-0049@4aa3a77e, J-2026-11-08-J@ef61624c) ; la règle s'est
donc soumise en entier dans D-0080, que Théo a validée. Elle est recopiée
ici mot pour mot, au nom du skill près.

## Décision

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
5. *Où elle vit.* Un skill du socle, `socle-resume` : une procédure écrite
   que l'agent charge quand il en a besoin, que l'installeur pose dans tout
   projet. Le moteur du socle, le programme qui fait les contrôles, n'en
   sait rien, et aucun contrôle ne prouve que l'agent l'applique. Hors
   d'une session cloud de Claude Code, le skill est inerte : l'outil qui
   programme un rappel n'y existe pas.

Le skill se nomme `socle-resume`, et non `socle-reprise` comme l'écrivait
D-0080 : ADR-0027@a8288770 met en anglais les noms de dossiers du socle, comme ceux
des trois autres skills. Un tour qui s'arrête pour une autre raison
qu'une limite, en attendant une action humaine par exemple, ne relance
jamais l'agent : ses réveils se retirent à sa fin (point 3), et un réveil
qui resterait vérifie la fin du tour d'avant (point 4) ; Théo l'a demandé
en validant (J-2026-11-08-K).

## Conséquences

Ce que la règle laisse passer, tel que D-0080 le dit : Trois cas ouvrent un tour d'une ligne : un
tour que vous interrompez sans réécrire avant la remise à zéro ; une étape
longue pendant laquelle tombe l'heure d'un réveil, qui attend la fin du
tour ; un réveil qui tombe pendant qu'un sous-agent tourne encore, le tour
fini. Plusieurs sessions coupées ensemble reprennent ensemble, et partagent
la fenêtre neuve. Une session que vous ouvrez ailleurs sans y avoir rien
poussé, l'agent ne la voit pas : les deux travailleraient en même temps.
Une session archivée (close dans l'application) : je n'ai pas mesuré si
ses réveils y tombent encore ; ils se suppriment dans la liste des tâches
programmées, sous le nom « Reprise après limite » suivi du projet.

Supposé : qu'un réveil, cinq minutes après la remise à zéro, trouve la
limite levée et reprenne la session, et qu'un sous-agent coupé fasse
refuser le tour qui attend son résultat ; la première coupure réelle le
dira, et B-0132 ne se ferme qu'alors. La défaire : une demande ; le socle
cesse de poser le skill, et un projet déjà équipé garde sa copie jusqu'à
ce que son humain la retire.
