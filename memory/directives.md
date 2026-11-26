<!-- socle: couche=consignes zone=publique -->
# Consignes

Les consignes durables de Théo, chacune avec son texte exact relu à sa source ; avant de s'appuyer sur une consigne, son texte exact se lit par `socle show C-NNNN`.

## C-0001 — Opus partout depuis le 12 novembre

> statut : en vigueur · source : D-0095, J-2026-11-12-L · date : 2026-11-10

> […] Les implémentations peuvent surement rester a opus (et passé cette semaine, j'utiliserai opus partout a nouveau de toute facon) […]

— D-0095, sur la semaine où Fable était offert.

> […] (btw on est à 77% d'utilisation fable, apres ce point cette conversation continuera sur Opus)

— J-2026-11-12-L.

## C-0002 — La roadmap demandée se donne au format court

> statut : en vigueur · source : J-2026-11-25-T · date : 2026-11-25

> Format court
>
> […]
>
> (Format court pour la roadmap)

— J-2026-11-25-T, après une roadmap détaillée.

## C-0003 — Atelier : prompt à copier, commutateur manuel tant que Théo jongle entre ses comptes

> statut : en vigueur · source : D-0173, D-0182, J-2026-11-24-BE · date : 2026-11-24

> Une fois que l'enchaînement de session sera complément implementé, pour l'atelier du socle nous resterons en mode manuel pour l'instant pour que je puisse jongler entre les comptes, bien que pour le socle enchainer et créer automatiquement reste le comportement par defaut du commutateur

— D-0173.

> 3 ok

— D-0182 : l'essai de la passation programmée dans l'atelier, quand Théo ne jongle plus entre ses comptes.

> […] Prompt a copier, j'avais dit dans une session précédente que pour l'instant le commutateur est en mode manuel

— J-2026-11-24-BE.

## C-0004 — Le hook de l'agent est terminé : rien sans preuve vue dans une session (ADR-0098)

> statut : en vigueur · source : J-2026-11-20-B, D-0143 · date : 2026-11-20

> Non mais en fait c'est la troisième fois qu'on dit qu'on arrête sur ce sujet exact donc la je veux une garantie qu'on va pas tourner en rond

— J-2026-11-20-B, sur le hook qui analyse les commandes.

> Je valide, et refuser pour D-0142

— D-0143, qui retient la règle qu'écrit ADR-0098 ; « refuser » vise D-0142.

## C-0005 — Du temps pour l'important, pas pour un cas limite rare ; revues, sous-agents, regroupements s'ils servent

> statut : en vigueur · source : D-0165, J-2026-11-25-P · date : 2026-11-24

> […] Allonger le temps de dev car on veut ajouter des choses importantes, corriger un bug important : pas de soucis
>
> Mais passer 10h sur un cas limite qui arrive rarement, et qu'en pratique n'est qu'une légère gêne pour l'agent qu'il peut gérer lui même c'est non

— D-0165.

> […] Je cherche a fonctionner de facon intelligente entre mettre des revues uniquement quand c'est necessaire/mieux, faire tourner des sous agents uniquement quand c'est necessaire/mieux, regrouper le travail intelligemment pour être efficace, sans alourdir inutilement le processus d'organisation […]

— J-2026-11-25-P.

## C-0006 — Revue de cap tous les trois lots ; pas dans le produit pour l'instant

> statut : en vigueur · source : D-0145, D-0183 · date : 2026-11-20

> Ok valider
> Et oui mettre ça dans le produit à terme si ça s'avère utile

— D-0145, qui valide la revue de cap : tous les trois lots ou à la clôture d'un jalon, au plus trois suggestions (le skill direction-review).

> Ok pour l'instant pas de revue de cap dans le produit, on se garde juste en tete que c'est une possibilité si le besoin vient plus tard (que je constate que les produits dans lesquels j'utilise le socle convergent mal ou dévident)

— D-0183.

## C-0007 — Un mot pour une chose ; une tâche rejoint sans demander le lot dont la règle s'applique

> statut : en vigueur · source : J-2026-11-16-I, J-2026-11-16-J · date : 2026-11-16

> […] Juste j'ai l'impression que ce qu'on appelle "sujet" maintenant correspond a ce qu'on appelait avant "lot", attzntion au vocabulaire, un mot veut dire soit une chose, soit une autre […]

— J-2026-11-16-I.

> Mais oui applique les, je t'ai demandé de faire des suggestions si ça va ensemble selon les regles qu'on s'était fixé (touche aux mêmes fichiers, etc) alors ça va ensemble
>
> Ça ne devrait même pas etre séparé si la regle qui fait que plusieurs choses appartiennent à un lot s'applique

— J-2026-11-16-J.

## C-0008 — Relecteur : le plus capable jusqu'à Opus ; Fable seulement si Théo le veut

> statut : en vigueur · source : D-0117, D-0119 · date : 2026-11-15

> Pour le modele relecteur : oui modele le plus capable dispo jusqu'à Opus,
> Si fable est dispo on le met pas par defaut (jsp si c'était clair pour toi), sauf si l'humain le veut
>
> […]

— D-0117.

> Si un lot est implémenté par fable (et bien le lot hein, pas la session d'orchestration), demander à l'utilisateur avant s'il veut aussi lancer fable sur la revue
>
> Btw je sais pas si t'avais en tête mais tout comme la revue, pour l'implementation on ne lance rien sur fable sauf si l'humain le veut
>
> […]

— D-0119.

## C-0009 — Tout ce qui est utile intègre le socle, règles du backlog comprises ; un sujet important se garde

> statut : en vigueur · source : J-2026-11-13-F, J-2026-11-14-K · date : 2026-11-13

> Tout ce qui est utile doit intégrer le socle, ouvre les points de backlog qu'il faut pour avoir en tête d'intégrer tout ça (ce qu'à fait b173 et les autres sujets) / […]

— J-2026-11-13-F.

> Ok, je comprends que l'ajout des projets comme chess ajoute beaucoup de sujets jusqu'à stabilisation, si un sujet est important on le garde, pas de débat la dessus

> (Btw ces questions pour le backlog sont valable sur le socle, pas que sur l'atelier évidemment, je sais pas si t'avais bien ça en tête)

— J-2026-11-14-K.

## C-0011 — Aucun autre dépôt dans la session, ni lecture de JustCook ou de theodubus/socle

> statut : en vigueur · source : J-2026-10-14-S, J-2026-11-09-M · date : 2026-10-14

> […] Juste fais gaffe, travailler avec d'autres repos c'est ce qui avait causé dans l'autre session le déplacement du dossier de conteneur par defaut dans la session précédent

— J-2026-10-14-S : un dépôt nécessaire se clone hors de la session, non déclaré racine.

> N'ajoute aucun autre dépôt à la session, et ne lis ni JustCook ni theodubus/socle (donner leurs liens reste permis).

— J-2026-11-09-M.

## C-0012 — Le pilote est un essai de choc pour le socle : pas grave s'il n'est pas idéal partout

> statut : en vigueur · source : J-2026-10-31-E · date : 2026-10-31

> […] Pas besoin de demander au pilote normalement il l'a fait et pas grave si le pilote n'est pas idéal partout, c'est un crashtest pour le socle donc normal / […]

## C-0013 — Documentation : plan soumis d'abord, ton formel, une question à un seul endroit, faite que validée

> statut : en vigueur · source : J-2026-10-20-Y, J-2026-10-21-A, J-2026-10-22-A · date : 2026-10-20

> non non, j'ai rien validé de ta documentation déjà (sauf si tu considérais ne pas avoir fini) / mais fais un effort sérieux / tes graphiques sont médiocre / […] fais un petit effort de conception sur ce qu'est censé être une documentation

— J-2026-10-20-Y.

> […] Le ton/vocabulaire : Plus formel/documentation et moins "explication à un collégien je t'explique et je te tutoie en m'adressant à toi", mais rester clair et compréhensible / […] il faut pas forcément un fichier par question, ça sert a rien de répondre partiellement à une même question dans plusieurs fichier. il faut se lister ce a quoi on veut répondre puis se dire ou ça a sa place et focus sur la compréhension de ces aspects aux endroits voulus. / tout est clair ? si tu préfère s'aligner, tu peux me faire un plan de ce que tu comptes faire dans le chat avant de refaire une nouvelle version

— J-2026-10-21-A.

> […] "éprouvé dans des projets jetables " Utile ? ici on dit qu'on l'a testé mais on ne dit pas a quoi sert l'outil / […] j'ai également l'impression que parfois on est très verbeux alors qu'en soit le fonctionnement est pas si compliqué, est ce que parfois c'est plus verbeux que nécessaire ? même dans help par ex, même si c'est décrit, j'ai du mal à me projeter dans le parcours utilisateur […]

— J-2026-10-22-A.

## C-0014 — Une limite proche peut décider de l'ordre, jamais de la qualité du travail ; passation avant elle

> statut : en vigueur · source : J-2026-11-09-C, J-2026-11-15-D, J-2026-11-16-W · date : 2026-11-09

> "Je reste sobre" => je dis pas de pas le faire, mais il ne faut pas que le fait de savoir qu'une limite arrive degrade la qualité du travail non plus / Si in travail demande effectivement plus de réflexion, alors tant pis il sera commencé à un moment et terminé apres la limite / Ça peut par exemple servir a prioriser les sujets le fait de savoir qu'on va peut être être coupé bientôt, mais jamais de faire une certaine partie du travail au rabais / […]

— J-2026-11-09-C.

> […] Explicite
>
> Car je ne veux pas que des lots soient  bâclés pour correspondre aux limites

— J-2026-11-15-D, sur la règle du modèle que l'agent résumait.

> Fais attention à la limite de session pour la passation

— J-2026-11-16-W.

## C-0015 — Une attente annoncée a son réveil programmé

> statut : en vigueur · source : J-2026-10-13-N · date : 2026-10-13

> Tu t'es pas programmé de réveil ? C'est fini la non ?

— J-2026-10-13-N, après un récap qui annonçait l'attente d'une CI.

## C-0016 — « Pour toi » : les seuls gestes de Théo, chacun redit en entier, sans renvoi plus haut

> statut : en vigueur · source : J-2026-10-14-F, J-2026-10-31-S, J-2026-11-24-AQ · date : 2026-10-14

> Alors là par exemple tes instructions sont pas claire par exemple. Je viens de faire b0056, tout est clair pour le coup ici sauf à la fin : "Ensuite, le lien moteur à la racine du dépôt peut partir ; l'agent le retire quand le verrou ne le nomme plus." Est ce que c'est un truc que je dois faire ? Si oui quoi ? Est ce que ça se fait tout seul ?? Et pas clair ton point relatif à b0058

— J-2026-10-14-F.

> Mais pourquoi poser une étiquette, c'est quoi une étiquette ??? Tu as peut etre expliqué tout ça y'a 3h dans ton chemin de pensee mais moi dans ton recap dire "je pose une étiquette" ne suffit pas du tout / […]

— J-2026-10-31-S.

> Alors tu as peut etre parlé de la regle en amont bien en haut dans ton travail, mais si tu me le remets pas dans le recap, c'est pénible pour moi d'aller scroller et rechercher l'info

— J-2026-11-24-AQ.

## C-0017 — Les heures données à Théo, à l'heure de Paris

> statut : en vigueur · source : J-2026-10-14-G · date : 2026-10-14

> Et quand tu donnes le temps écris en heure de paris stp

## C-0018 — Une branche à supprimer se vérifie d'abord sur GitHub

> statut : en vigueur · source : J-2026-11-18-T · date : 2026-11-18

> Pourquoi tu continues de me demander de supprimer des branches que j'ai deja supprimé et que tu ne prends que l'info quand je te le dis alors que tu as accès à la liste des branches existantes sir github

— J-2026-11-18-T (B-0193).

## C-0019 — Pas de rétro-compatibilité avec une version antérieure du socle

> statut : en vigueur · source : J-2026-10-19-A · date : 2026-10-19

> […] Et d'une manière général ne te mets pas des éléments de backlog de rétro-compatibilité avec une version antérieure / Le projet est EN DEV / C'est en privé et personne ne l'utilise pour le moment / Ne te mets pas ces contraintes la sinon on s'en sort pas, considere que pour le moment personne ne l'a encore utilisé

## C-0020 — Le but et le tri : `docs/fabrication/but-et-tri.md` ; un récap à Théo avant tout abandon

> statut : en vigueur · source : D-0167 · date : 2026-11-24

> Je valide les critères, et la description 1, c'est pas mal le "revient s'il est vu"
>
> Lors du tri, je voudrais avant abandon un recap de l'agent ce ce qu'on abandonne
>
> […]

— D-0167, qui valide la description du projet et les critères de tri.

## C-0021 — Sessions d'agent réel sur l'abonnement, chacune plafonnée à l'équivalent de 2 dollars

> statut : en vigueur · source : D-0009, J-2026-10-19-H · date : 2026-10-11

> D0009 validé pour 18 sessions. […]

— D-0009 : le banc sur un agent réel, chaque session à l'équivalent de 2 dollars au plus, sa consommation rapportée.

> […] Tu as mon autorisation pour utiliser l'abonnement / […]

— J-2026-10-19-H : les sessions qui éprouvent B-0069, plafonnées comme au banc.

## C-0022 — En autonomie sur le backlog, sauf besoin d'un arbitrage

> statut : en vigueur · source : J-2026-10-20-C · date : 2026-10-20

> […] Et apres ça tu peux travailler en autonomie sur la backlog sur tous les éléments qui peuvent se faire n'importe quand et pour lesquels tu n'as pas besoin d'arbitrage / Tu peux t'arrêter quand tu as fini ça ou quand tu as besoin d'un arbitrage

## C-0023 — Une demande de Théo se lit pour son besoin, pas à la lettre

> statut : en vigueur · source : J-2026-11-25-K · date : 2026-11-25

> Pourquoi tu avais repris ma demande littéralement sur "reprends" alors qu'en soit la question de fond etait assez évidente pour le fait de juste avoir besoin de faire reprendre sans avoir les infos
>
> Quel intérêt y aurait t il eu a figer sur uniquement "reprends" ?

## C-0024 — Corriger et stabiliser avant chess ; chess mis à jour d'un coup, ses corrections ; puis les nouveautés

> statut : en vigueur · source : J-2026-11-13-I, J-2026-11-13-L, J-2026-11-21-B · date : 2026-11-13

> Ok pour moyenne sur B-0204 et B-0205 et ok pour tes propositions de priorité, bien garder en tête ce set d'éléments de backlogs (qui peut réduire ou grossir en fonction des trouvailles) à faire avant de repasser à l'ajout de feature classiques
>
> […]

— J-2026-11-13-I.

> […] je mets pas a jour tout de suite j'attends qu'on implemente tout pour pas avoir a faire 150 mises à jour critiques […]

— J-2026-11-13-L, sur la mise à jour de chess.

> […] Moi je veux juste finir à corriger et stabiliser le socle avant chess, puis le mettre à jour d'un coup, éventuellement corriger le socle suite à la mise à jour et ensuite reprendre le reste du développement qui relève davantage d'ajout de features
>
> Donc débrouille toi revois les jalons si besoins mais je veux tous les besoins/taches de correction/stabilisation du produit avant chess, puis le reste apres
>
> […]

— J-2026-11-21-B.

## C-0025 — En session web, la branche donnée à supprimer ne dit pas que le proxy a refusé sa suppression

> statut : en vigueur · source : J-2026-11-26-L · date : 2026-11-26

> Proxy refusé pour supprimer la branche : inutile de le préciser si on est en session web

— J-2026-11-26-L, sur le récap qui lui donnait `ccr-0451fbf2-5mg4au` à supprimer en disant le refus du proxy cloud.

## C-0026 — Session unité de budget : sous 150 000 jetons, elle enchaîne les lots, sinon elle range

> statut : en vigueur · source : D-0194, D-0195, D-0210 · date : 2026-11-26

> […] Oui je retiens cette réforme

— D-0194 : la réforme de l'organisation, dont la session unité de budget.

> Je valide

— D-0195 : la page `docs/fabrication/organisation-proportionnee.md` et ses seuils.

> Valider D120

— D-0210, la seule demande alors en attente : le seuil de contexte baissé de 300 000 à 150 000 jetons, sur les mesures de l'usage.
