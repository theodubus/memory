<!-- socle: couche=decisions zone=publique -->
# ADR-0058 — Les lignes d'empreinte d'une demande ne comptent pas dans son budget, et la commande qui pose une demande en dit le contrat

> statut : acceptée · date : 2026-11-10 · source : B-0149@28c35de2 · lu : decisions@35d8ea05

## Contexte

La demande qui approuve une mise à jour cite chaque fichier protégé
changé avec son empreinte nouvelle : c'est ce que `protege.fichiers` y
cherche. Le lint tenait chaque empreinte pour un identifiant interne, à
décrire en cinq mots au moins. Pour les 54 fichiers du pilote, la liste
pesait plus de la moitié du budget d'une demande (12 000 octets), dépassé
de 374 octets : l'agent a retiré un paragraphe utile de son contexte, dont
le contrat, trois paragraphes d'ouverture (ADR-0046@1017e7f0), ne lui est
apparu qu'au refus du lint (J-2026-11-10-H@a5473f3b, B-0149@28c35de2).

L'humain ne lit pas ces empreintes : il lit les fichiers dans la pull
request (D-0071@9b06b40c). Le budget d'une demande borne ce qu'il doit
lire ; la liste, elle, est écrite pour le contrôle.

Le pilote donnait trois pistes : sortir la liste du budget, accepter une
forme courte (chemin et empreinte), ou une commande qui écrit la liste
dans la demande. Un projet reçoit 92 fichiers de moteur, tous protégés :
réduite au chemin et à l'empreinte, la liste d'une mise à jour qui les
change tous pèse encore 7 Ko, et laisse au reste moins que ce que le
pilote avait. La forme courte seule ne tient donc pas. Une commande qui
écrit la liste n'en change pas la taille, et `socle check` donne déjà
chaque chemin avec son empreinte.

## Décision

1. Une **ligne d'empreinte** est une ligne d'une demande qui ne dit
   qu'un fichier protégé et son empreinte nouvelle (`sha256:` et seize
   caractères, ou « supprimé »), dans un ordre ou dans l'autre, en puce,
   entre accents graves ou dans un tableau. Elle ne compte pas dans le
   budget de la demande, et le lint ne demande pas de décrire son
   empreinte : le chemin dit ce qu'elle est. Un mot de plus sur la ligne,
   ou un chemin que la politique ne protège pas, et c'est de la prose,
   décrite et comptée comme avant.
2. `socle new request` imprime le contrat d'une demande sous
   l'identifiant, avec les seuils du lint et le budget du projet ; en
   session cloud, « Et maintenant » dit de poser par elle la demande d'une
   mise à jour, et d'y écrire chaque fichier sur sa ligne d'empreinte. Le
   refus d'une demande au-delà de son budget dit la même issue, au lieu
   d'« archiver dans le journal ».

La première piste est retenue, la forme courte lui servant de
définition : c'est la seule qui tienne quel que soit le nombre de
fichiers, sans commande nouvelle ni changement des garde-fous d'un projet
équipé.

## Conséquences

Une demande d'approbation garde tout son budget pour son contexte, que
la mise à jour change 5 fichiers ou 100. La règle vaut dès la mise à
jour qui l'apporte : c'est le moteur nouveau qui juge la demande qui
l'approuve. Ce que le budget ne compte plus est borné : une ligne
d'empreinte ne porte aucune prose, et son chemin doit être protégé.

Le défaire : `ligne_d_empreinte`, `hors_empreintes` et `contrat` dans
`engine/socle/requests.py`, leur emploi dans le contrôle des budgets, le
lint et `socle new request` ; leurs tests dans `tests/test_demandes.py`,
le défaut `empreintes-bavardes` et son témoin dans l'auto-test.
