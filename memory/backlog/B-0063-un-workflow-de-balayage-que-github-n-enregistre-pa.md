<!-- socle: couche=backlog zone=publique -->
# B-0063 — Un workflow de balayage que GitHub n'enregistre pas reste un simple avertissement

> statut : ouvert · origine : J-2026-10-15-D · lu : backlog@acfaabc5

Constaté le 15 oct. dans le dépôt d'essai : GitHub n'a pas enregistré le
workflow du balayage de mutation (`socle-mutation.yml`), pourtant présent
sur la branche par défaut ; l'onglet Actions ne montre que « Socle », et
l'API rend 404. Le contrôle `mutation.vivante` lit ce 404 comme « pas
encore sur la branche par défaut » et n'avertit que : un projet neuf dans
ce cas n'aurait jamais de balayage, sans que la CI échoue jamais. Faire
la différence entre « pas encore fusionné » (le fichier absent de la
branche par défaut) et « présent mais inconnu de GitHub », qui doit
échouer au-delà d'un délai, avec le remède ; chercher d'abord comment
GitHub enregistre un workflow sans déclencheur `push` (supposé : il ne le
fait pas au premier push d'un dépôt neuf).

Vérifié le 15 oct. par la session d'essai, sans rien pousser : sur GitHub,
la branche par défaut du dépôt d'essai porte `socle-mutation.yml`, du même
blob que le projet local (3545cfd), poussé dans le premier commit ; 22
minutes après le push, la liste des workflows ne compte que « Socle », sans
même une entrée en erreur pour le balayage. Supposé : GitHub n'enregistre
au premier push d'un dépôt vide que le workflow que cet événement
déclenche ; un workflow planifié le serait au push suivant sur la branche
par défaut. À éprouver par un commit anodin sur cette branche du dépôt
d'essai, puis relire la liste ; si c'est confirmé, un projet neuf dont le
premier push porte le socle n'a pas de balayage tant que personne ne
repousse, et le contrôle doit le dire.
