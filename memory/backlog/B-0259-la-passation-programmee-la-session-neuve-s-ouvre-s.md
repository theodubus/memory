<!-- socle: couche=backlog zone=publique -->
# B-0259 — La passation programmée : la session neuve s'ouvre seule à la remise à zéro de la fenêtre, au lieu d'un prompt à copier

> statut : ouvert · origine : J-2026-11-16-E · ref : B-0156 · lu : backlog@dbfb9832

D'une analyse en lecture seule du 15 novembre sur d1d296e, que Théo a
fait inscrire (J-2026-11-16-E) ; il n'en fixe ni la priorité ni le lot.
Il précise B-0156@15e2df3a (le relais de session par l'agent, l'une de
ses pistes). Rien n'y est testé : ce qui est marqué « lu » vient de la
description des outils de la session cloud.

Le problème. Près d'une limite, l'agent range, puis donne à Théo le
prompt de la session suivante à coller (`.claude/skills/socle-batch/SKILL.md`,
« Changer de session »). S'il crée lui-même la session avant la remise à
zéro, elle n'a pas de quota. S'il attend d'être réveillé après, il relit
sa conversation à froid.

La piste. Programmer n'est pas créer. Pendant le rangement, l'agent
programme l'ouverture de la session neuve à la remise à zéro plus cinq
minutes, l'heure que lit déjà `.claude/skills/socle-resume/SKILL.md`.
L'ancienne session n'est jamais réveillée.

La variante visée, B (deux appels) : `create_session` sans prompt, avec
son modèle, puis `create_trigger` avec `persistent_session_id` et
`run_once_at`, qui y envoie le prompt de passation. Lu : le mode de
permission est hérité de la session qui crée ; la session existe aussitôt,
et son lien se donne dans le récap ; pas de notification sur le téléphone
de Théo dans ce mode ; la session qui crée peut recevoir un tour si celle
qu'elle a créée échoue.

Le repli, A (un appel) : `create_trigger` avec `create_new_session_on_fire`
et `run_once_at`. Lu : accepte une notification sur le téléphone ; n'a pas
de paramètre de modèle ; supprimer la tâche supprime la session qu'elle a
ouverte. Non dit : le mode de permission et la branche de la session
ouverte.

Les inconnues à lever par un essai, avant toute spécification. La session
d'essai ne fait que répondre, sans rien écrire ni pousser : son modèle, sa
branche, si l'état du socle a été injecté au démarrage, son mode de
permission, ses outils de session. Pour B :

1. La session créée sans prompt reçoit-elle le prompt programmé cinq
   minutes plus tard, et travaille-t-elle sans attendre une approbation ?
2. A-t-elle le dépôt et les hooks du socle, et sur quelle branche ?
3. Son modèle est-il celui demandé à sa création ?
4. L'ancienne session est-elle réveillée par quoi que ce soit venu de la
   nouvelle : sa fin de tour, ou un échec s'il se provoque sans risque ?
5. Une session laissée vide une nuit reçoit-elle encore son prompt ?
6. Annuler (supprimer la tâche, archiver la session vide) : cela
   marche-t-il, et que reste-t-il dans la liste de Théo ?
7. Ce que le tout coûte, en part de la fenêtre de cinq heures.

Pour A, seulement si B échoue sur un point qui l'empêche : le modèle, le
mode de permission et la branche de la session ouverte.

La règle de choix. B si ses inconnues 1 à 5 se lèvent. Sinon A, si les
siennes se lèvent. Sinon le prompt à copier reste, et le sujet le dit.
Une seule variante s'implémente. L'agent montre le relevé à Théo, qui
confirme le choix.

Le commutateur. Deux modes, que Théo change en le disant dans la
conversation, consignés au chantier actif : « prompt à copier » (plusieurs
comptes ; par défaut, à confirmer dans la spécification) et « session
programmée ». Pour qu'aucun travail ne se fasse en double :

- changer de mode annule ce qui est programmé, et le dit ;
- une session programmée commence par vérifier que personne n'a avancé
  depuis la passation (le commit que nomme son prompt) ; sinon elle ne
  fait rien et le dit ;
- le réveil après limite reste le secours des deux modes. À vérifier : sa
  garde « une autre session a poussé sur la branche » voit-elle une
  session qui a continué sur sa propre branche, puisque chaque session a
  la sienne.

## Satisfait quand

- [ ] près d'une limite, quand Théo a choisi ce mode, la session neuve s'ouvre seule à la remise à zéro de la fenêtre, sans prompt à coller ni travail fait en double ; si aucune variante ne tient à l'essai, le prompt à copier reste, et le besoin le dit
