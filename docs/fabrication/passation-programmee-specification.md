# La passation programmée : spécification

Soumise à Théo le 24 novembre 2026, avant son code, par la demande qui
remplace D-0160 (T-0039, T-0041, T-0080). Elle répond à B-0156 et à
B-0259 ; l'essai qui la fonde est relevé dans
`docs/fabrication/passation-programmee.md`. Les heures du prompt sont en
UTC ; celles que lit l'humain, à l'heure de Paris.

## Ce qu'elle fait

Une session qui orchestre ne mène qu'un lot. Quand elle doit s'arrêter
(son lot livré, une limite d'usage proche, une longue attente), elle
range, puis, au lieu de donner à l'humain le prompt de la session
suivante à coller, elle crée elle-même cette session et programme son
prompt pour l'heure qui convient. La session neuve repart de la mémoire
du dépôt, comme celle que l'humain ouvre.

## Ce qu'elle coûte

Ce que coûte une session que l'humain ouvre : son démarrage, environ
1,1 point de la fenêtre de cinq heures (E1), puis son travail. Une tâche
menée par un sous-agent y coûte de 3 à 4 points de la semaine, le
relecteur d'un lot 3 (J-2026-11-13-E), un lot entier de 8 à 16 points de
la semaine. Ce qu'elle évite : le compactage d'une conversation chaude,
environ 8 points de la fenêtre avec l'appel qui le suit, ou sa relecture
à froid après une pause, de 7 à 39 points
(`docs/fabrication/consommation.md`).

## Les deux modes

- **Session programmée** : l'agent crée la session suivante et programme
  son prompt. C'est le mode par défaut du produit (D-0161, D-0173).
- **Prompt à copier** : l'agent donne le prompt dans son récap, et
  l'humain ouvre la session lui-même. C'est le mode de qui a plusieurs
  comptes ou veut contrôler l'enchaînement, et celui de ce dépôt
  (D-0173).

Le mode est celui que dit une consigne du chantier actif ; sans
consigne, la session programmée. L'humain le change en le disant dans la
conversation ; l'agent écrit la consigne au chantier actif et son texte
exact au journal. Passer au prompt à copier annule ce qui est programmé
(la tâche supprimée, la session vide archivée) et le dit, avec le lien de
chaque session annulée.

Le prompt à copier s'applique aussi, et le récap le dit, quand l'agent ne
peut pas programmer : hors d'une session cloud de Claude Code, sous un
autre agent, ou quand la création est refusée.

## Quand

| Le moment | L'heure de la session suivante |
| --- | --- |
| Lot livré | tout de suite : la minute qui suit |
| Rangement à dix points d'une limite (`socle-batch`) | la remise à zéro de cette fenêtre, plus cinq minutes |
| Avant une attente de plus d'une heure (une CI longue, une heure donnée) | la fin de l'attente |

Une session ne part jamais sur une fenêtre au-delà de son seuil, 15 % de
la fenêtre de cinq heures et 75 % de la semaine : l'heure du tableau
recule alors à la remise à zéro de cette fenêtre plus cinq minutes, la
semaine si c'est elle. Les seuils viennent de la question de Théo du
23 novembre (J-2026-11-23-J) : un lot coûte de 60 à 115 points de la
fenêtre de cinq heures et de 8 à 16 points de la semaine, et le
rangement commence à dix points d'une limite ; une session lancée sur
une fenêtre déjà entamée serait coupée en cours de lot. Le seuil de la
semaine est aussi celui au-delà duquel `socle-batch` ne lance déjà plus
qu'un sous-agent.

## Les bornes d'une chaîne sans l'humain

La chaîne ne programme pas la session suivante, et le récap donne le
prompt à copier :

- quand le lot suivant n'a aucune tâche prête dans l'état, parce qu'une
  décision revient à l'humain ou que rien n'est prêt ; une demande en
  attente qui ne le bloque pas ne l'arrête pas, comme aujourd'hui
  (politique d'autonomie, point 8) ;
- après deux lots menés sans message de l'humain, le lot en cours
  compris, soit au plus de 16 à 32 points de la semaine : le prompt
  programmé porte le compte (« chaîne : n ») ; le prompt à copier porte
  0, et une session dans laquelle l'humain a écrit repart de zéro ;
- quand la plateforme refuse de créer une session (supposé : une
  profondeur de huit sessions créées l'une par l'autre ; `get_session`
  donne `lineage`, profondeur 0, limite 8, pour une session que l'humain
  a ouverte).

## La façon : la variante B, en deux appels

Les inconnues 1 à 5 de B-0259, celles que sa règle de choix exige, sont
levées par l'essai : la première pour la lecture, la deuxième à condition
de nommer la branche, la quatrième pour une fin propre ; la sixième
(annuler) l'est aussi, et la septième pour le coût du démarrage (le
relevé, « Après coup »). A, le repli, n'est ni essayée ni implémentée.

1. **Ranger**, comme aujourd'hui, l'entrée du journal qui dit la
   passation comprise, sans les identifiants que seul le récap donnera ;
   retirer les réveils de la session ; puis **pousser**. Rien ne se
   pousse plus après l'étape 4 : le prompt nomme la tête distante et ne
   se récrit plus une fois programmé (`update_trigger` le refuse depuis
   la session qui l'a créé). Un commit nécessaire ensuite annule la
   passation (la tâche supprimée, la session archivée), qui se refait.
2. **Le prompt** : `python3 .socle/socle handoff prompt` l'imprime, avec
   sa garde (plus bas).
3. **`create_session`**, sans prompt : `source_url` le dépôt ;
   `source_revision` la référence que la garde nomme (`--ref`, plus bas) ;
   `outcome_branch` la branche de travail (sans elle, la session neuve
   n'a pas où pousser : E1, E4) ; `model` celui de la session ; `effort`
   celui de la session, qui ne s'hérite pas (E1), et l'appel se refait
   sans lui s'il le refuse ; `title` « Passation — <lot> — part le
   <jour> à <heure de Paris> » ; l'étiquette `passation`.
4. **`create_trigger`** : `persistent_session_id` la session créée,
   `run_once_at` l'heure du tableau, `prompt` le texte de l'étape 2.
5. **Le récap** donne le lien de la session, son heure et comment
   l'arrêter ; `Ensuite :` le dit.

Si un appel échoue : la session créée s'archive, et le prompt à copier
remplace la passation, le récap disant pourquoi.

## Le prompt et sa garde

`socle handoff prompt` imprime le prompt de la session neuve d'aujourd'hui,
précédé de la passation et de sa garde :

```text
Passation de <lien de la session qui part> — <dépôt>, à <heure UTC>.
Avant tout : git fetch origin, puis
python3 .socle/socle handoff check --ref origin/<branche> --head <sha> --since <heure UTC>
S'il refuse, ne rien faire d'autre que le dire.
Chaîne : <n> lot(s) mené(s) sans message de l'humain.
Reprends le travail de ce dépôt, en session neuve.
[la suite du prompt d'aujourd'hui : l'état, le chantier actif, le lot, ce qui attend]
```

`--ref` est la branche de travail, ou la branche par défaut si la pull
request du lot vient d'être fusionnée ; `--head`, sa tête poussée.
`socle handoff check` refuse, en disant pourquoi :

- si la tête de `--ref` n'est plus `--head` : quelqu'un a poussé depuis
  la passation ;
- si une autre branche distante porte un commit daté d'après `--since`
  qui touche `memory/` sans être un ancêtre de `--head` : une autre
  session travaille sur le projet, puisqu'un agent sous le socle écrit
  toujours sa mémoire ; les commits d'un robot de dépendances ne la
  touchent pas.

La pull request du lot fusionnée pendant l'attente par un commit de
fusion n'arrête pas la session : `--head` est alors un ancêtre de la
branche par défaut, et la session repart de celle-ci. Fusionnée par
squash, la garde refuse ; la session le dit, sans dommage.

Accepté, la session neuve se place sur la tête distante de sa branche :
son clone date de sa création, pas de son prompt (E2). Le même prompt
sert au mode « prompt à copier » : collé tard, il trouve de même une
branche qui a bougé. La garde est un contrôle nouveau : son défaut
injecté et son témoin sain vont à l'auto-test. La reprise de
`socle-resume` l'appelle aussi, avec la tête distante lue avant son
`git fetch` et l'heure de la coupure.

## La pull request ouverte

Le lot suivant s'ajoute à la pull request ouverte, comme aujourd'hui
quand l'humain garde la même session. Une session partie d'un prompt de
passation que la garde accepte, programmé ou collé par l'humain, a
l'autorisation d'y continuer, que demande aujourd'hui une session neuve
qui trouve ouverte la pull request d'une autre : c'est l'enchaînement
qu'il a choisi (D-0161), ou le prompt qu'il a collé lui-même. Cette pull
request devient celle de la session neuve : elle peut la fusionner, si
la politique le permet à l'agent, aux mêmes conditions ; sinon l'humain
la fusionne. Le gabarit d'`AGENTS.md` et le guide le disent.

## Voir et arrêter

- La session créée se voit aussitôt dans la liste de l'humain, avec son
  titre, « prête à relire » tant qu'elle attend son prompt (E1 à E3). Son
  dernier message dit ce qu'elle a fait, pourquoi la chaîne s'arrête ou
  ce que la garde a refusé, et ce qui revient à l'humain ; l'essai n'a
  montré aucune notification sur son téléphone.
- Pour l'arrêter : écrire « arrête » dans la session qui l'a programmée,
  tant qu'elle tourne ; ensuite, changer de mode dans n'importe quelle
  session du projet, ou supprimer sa tâche dans la liste des tâches
  programmées du compte et archiver la session.
- Une session que l'humain ouvre pendant qu'une passation attend la voit
  au démarrage et la lui dit, avec son heure ; elle ne l'annule que s'il
  le demande. Le skill `socle-resume` lit déjà les tâches programmées au
  premier tour, mais n'y garde que ses réveils : il y ajoute les
  passations qui attendent. Si cette session pousse avant l'heure, la
  garde arrête la session programmée ; si elle n'a rien poussé, seul ce
  signalement l'évite.

## Ce qui reste

- **Le secours.** Les réveils du skill `socle-resume` restent, dans les
  deux modes : une session coupée avant d'avoir rangé reprend à la
  remise à zéro.
- **L'ancienne session réveillée.** Selon la documentation de l'outil, un
  tour en échec ou un conteneur redémarré dans la session neuve donne un
  tour à celle qui l'a créée (inconnue 4, non provoquée). Elle le dit en
  une ligne et ne fait rien d'autre ; le coût, une relecture à froid de
  sa conversation, est rare, et accepté.
## Où cela s'écrit

- Un skill nouveau du produit, `socle-handoff`, en français et en
  anglais : les modes, le moment, les bornes, les deux appels, le récap.
  « Changer de session » de `socle-batch` s'y réduit à ranger, puis à
  suivre ce skill : les gabarits de `socle-batch` et de `socle-resume`
  sont à quelques octets de leur plafond de 8 000.
- `socle handoff prompt` et `socle handoff check`, dans le moteur, qui ne
  connaissent que git et la mémoire ; leurs tests, et le défaut injecté
  de la garde.
- Le gabarit d'`AGENTS.md` (la liste des skills, la pull request d'une
  passation), `HELP.md` (les deux modes, comment changer), une note de
  version en français et en anglais.
- Deux tests de `tests/test_skills.py` qui listent les skills du produit
  changent de valeur attendue, sur l'accord de Théo à la demande qui
  soumet cette spécification.
- Dans ce dépôt, le mode reste le prompt à copier (D-0173).

Ce découpage revient à T-0079 (le skill, sur la réponse à la demande) et
à T-0081 (la commande et sa garde, le mode, l'annulation).

## Non essayé

Vérifié par les tests de T-0081 pour ce qui se teste sans la plateforme ;
le reste se voit au premier usage réel, chess après sa mise à jour, où le
défaut s'applique :

- une session créée sur une branche qui existe déjà sur GitHub
  (`source_revision`) ; E4 n'a essayé qu'une branche neuve ;
- l'écriture et le push sans approbation dans la session neuve : l'essai
  n'a fait que lire, en mode `auto` hérité ;
- la profondeur maximale d'une chaîne de sessions ;
- `effort` passé à `create_session` quand l'appel est pré-approuvé, ce
  que l'outil dit refuser.
