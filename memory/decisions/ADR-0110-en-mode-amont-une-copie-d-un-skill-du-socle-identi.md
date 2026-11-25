<!-- socle: couche=decisions zone=publique -->
# ADR-0110 — En mode amont, une copie d'un skill du socle identique à son gabarit, et un test dont ne changent que des phrases du texte d'un skill du produit, passent sans validation de l'humain

> statut : acceptée · date : 2026-11-25 · source : B-0353@b2e1a9d4, D-0197@490ec951, D-0196@282f8a66, J-2026-11-25-T@7fe30539, ADR-0098@3081a5ed, ADR-0078@a50bf2ef, D-0175@6ad5e987, D-0188@e76c686a · lu : decisions@6f9fc52a

## Contexte

Chaque lot qui change un skill du produit finit sur une demande à Théo :
remettre les copies protégées de `.claude/skills/socle-*/` et changer les
tests qui lisent leur texte (D-0196@282f8a66, comme D-0175 et D-0188).
Théo, le 25 novembre : « C'est pénible de valider a chaque fois les
skills, alors qu'en soit moi humain ne suis pas plus capable de dire s'ils
sont bons ou pas, c'est l'expérience qui le dit » (J-2026-11-25-T@7fe30539).
À la question d'intention de B-0353@b2e1a9d4, il retient l'option A
(D-0197@490ec951) : dans ce dépôt seulement, les copies suivent leur
gabarit relu dans le lot, et les tests qui ne lisent que leur texte se
changent sans sa validation ; dans chess, rien ne change.

En mode amont, l'agent écrit lui-même les gabarits
(`engine/socle/templates/skills/`), et `protege.fichiers` laisse déjà
passer tout changement du paquet `engine/socle/` : la protection de la
copie n'ajoute qu'une signature. Les tests lisent le texte que pose
l'installeur (`installer.poser_skills`), c'est-à-dire le gabarit ; ceux de
D-0196 en attendaient des phrases que le lot avait récrites.

## Décision

1. **Les copies.** En mode amont, `protege.fichiers` laisse passer sans
   demande le changement d'une copie `.claude/skills/socle-<nom>/SKILL.md`
   qui est, à la révision jugée, identique octet pour octet à son gabarit
   de la même révision, celui que l'installeur pose : `<moteur>/socle/
   templates/skills/socle-<nom>/SKILL.<langue>.md` dans la langue de la
   mémoire s'il existe, `SKILL.md` sinon. Une copie retirée passe si son
   gabarit l'est aussi. Le contrôle le dit en avertissement. Toute autre
   écriture de la copie reste refusée, comme avant.
2. **Le geste ne change pas.** La copie se remet par l'installeur relancé
   dans le mode de son verrou (`install --target . --mode amont`) ; le
   hook de l'agent refuse toujours de l'écrire autrement, et ne change pas
   (ADR-0098@3081a5ed). Ce que l'installeur réécrit d'autre suit ses
   propres règles.
3. **Les tests du texte.** En mode amont, `tests.attendus` laisse passer
   sans validation un test supprimé, ou une assertion changée ou retirée,
   quand les phrases qu'il perd suivent le texte d'un skill du produit :
   - ses phrases : les chaînes littérales des assertions perdues (du test
     entier, s'il est supprimé), sans leurs guillemets, blancs réduits,
     d'au moins douze caractères ; il en faut une au moins ;
   - chacune était, à la base, dans le texte d'un gabarit de skill du
     produit (`<moteur>/socle/templates/skills/*/SKILL*.md`) que la plage
     change, blancs réduits ;
   - aucune n'était, à la base, dans un module Python du moteur
     (`<moteur>/socle/**/*.py`) : une phrase que le moteur imprime est un
     comportement, pas le texte d'un skill ;
   - l'une au moins n'est plus dans aucun gabarit de skill à la révision
     jugée : le test suit un gabarit qui s'en est écarté.

   Le contrôle dit en avertissement quel gabarit le test suit. La même
   règle tait l'avertissement des valeurs changées hors des assertions,
   pour les valeurs qui la suivent.
4. **En mode projet, rien ne change** : chess et tout projet installé
   gardent la demande. Aucune note de version, faute de changement pour
   un projet installé (ADR-0078).
5. **Le skill de l'atelier** `delegate-lot` dit la remise sans demande ;
   les tests des skills de l'atelier (`delegate-lot`, `direction-review`)
   restent sous la règle commune : D-0197 ne porte que sur les skills du
   socle.

## Modèle de menace

Ce que l'agent pourrait faire : (a) donner à une copie protégée un texte
autre que celui de son gabarit, pour se donner une autre procédure que
celle que le lot relit ; (b) affaiblir le test d'un comportement du moteur
sous couvert du texte d'un skill ; (c) changer le test d'un skill pour
laisser passer une régression du skill.

Fermé :

- (a) La copie n'est acceptée qu'identique à son gabarit de la même
  révision. Le gabarit est dans le diff du lot, sous la revue que le lot
  justifie ; une copie qui diffère d'un seul octet reste refusée.
- (b) Les phrases perdues doivent avoir été du texte d'un gabarit de
  skill, jamais d'un module Python du moteur, et le gabarit doit s'être
  écarté de l'une d'elles. Le test d'un message du moteur perd une phrase
  écrite dans un module : refusé. Une assertion sans phrase (un nombre,
  une clé courte) : refusée.

Laissé ouvert, et pourquoi c'est accepté :

- (c) L'agent peut changer ensemble le gabarit, sa copie et ses tests :
  c'est la décision de Théo, qui ne juge pas mieux le texte d'un skill ;
  l'expérience et la revue du lot le jugent. Le gabarit vit déjà dans
  `engine/socle/`, libre en mode amont.
- Une phrase à la fois dans un gabarit de skill et dans une
  documentation (le guide, le gabarit d'`AGENTS.md`) : le test de la
  documentation qui la perd passe aussi. C'est du texte de même nature.
- Un test qui lit un skill et juge aussi un comportement : seules ses
  assertions perdues se jugent ; celle du comportement, inchangée, reste
  sous la règle commune.
- Le mode amont se lit dans le verrou du moteur, un fichier protégé :
  l'agent ne fait pas passer un projet en amont sans l'humain.
- Les guillemets s'ôtent sans connaître le langage (un préfixe de
  lettres, puis les mêmes guillemets aux deux bouts) ; une chaîne à
  échappements ne se retrouve pas dans le gabarit et reste refusée : la
  règle n'échoue que du côté strict.

## Conséquences

Un lot qui change un skill du produit relance l'installeur en mode amont,
et les copies et les tests de leur texte se commitent sans demande ; le
récap le dit. Les fichiers que l'installeur réécrit d'autre restent sous
leurs règles. Pour défaire : retirer les deux exceptions du code ; les
demandes reviennent.
