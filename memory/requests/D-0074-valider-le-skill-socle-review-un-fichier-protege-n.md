<!-- socle: couche=demandes zone=publique -->
# D-0074 — Valider le skill socle-review : un fichier protégé nouveau de ce dépôt, et deux tests qui comptent un skill du socle de plus (B-0124)

> date : 2026-11-02

## Décision demandée

Valider le skill `socle-review`, écrit selon la spécification que vous avez
validée (ADR-0042) : il ajoute un fichier protégé à ce dépôt,
`.claude/skills/socle-review/SKILL.md`, et change la valeur attendue de
deux tests, `test_l_installeur_les_pose_et_la_politique_les_protege` et
`test_dans_les_deux_langues_ils_passent_leurs_controles`, qui comptent les
skills du socle.

## Contexte

Vous avez validé la spécification de la revue adversariale (D-0072) : avant
le push d'un lot qui change du code, une spécification ou un test, l'agent
le fait relire par un sous-agent sans contexte. La commande `socle review`,
qui prépare le dossier du relecteur, est livrée. Reste le skill qui dit à
l'agent quand et comment s'en servir. L'installeur le pose dans tout projet,
comme les deux autres skills du socle, et la politique le protège. Deux
choses exigent votre accord :
- le fichier `.claude/skills/socle-review/SKILL.md` de ce dépôt est
  protégé : l'installeur, relancé ici, l'a posé, avec l'empreinte
  `sha256:0ce646d6544049a5` ;
- deux tests de `tests/test_skills.py` comptent les skills du socle : la
  liste attendue gagne `socle-review`. La politique, au point 2, veut une
  demande validée qui nomme un test dont la valeur attendue change.

Le skill entier est recopié plus bas : il n'est pas encore sur GitHub, car
ses tests échoueraient sans votre réponse. Sont prêts aussi : la ligne qui
le nomme dans les instructions posées dans un projet, sans l'y exiger, et
la règle qui l'applique aux lots de ce dépôt.

Le skill, tel que l'installeur le pose en français :

```markdown
---
name: socle-review
description: Faire relire un lot par un relecteur sans contexte avant de le livrer, la revue adversariale, puis traiter ses constats. À utiliser avant le push qui livre un lot qui change du code, une spécification ou un test, dans un projet qui l'applique.
---

# La revue adversariale d'un lot

Les contrôles du socle jugent la forme du travail ; la revue en juge le
fond, par un relecteur qui ne partage pas les angles morts de l'agent qui
a écrit le lot, et qui cherche à le prendre en défaut.

## Quand

Avant le push qui livre un lot qui change du code, une spécification ou un
test ; jamais pour un lot qui ne touche que la mémoire. Une seule passe par
lot : pas de seconde revue après les corrections.

## Comment

1. Commiter le lot : la revue ne voit que ce qui est commité, ou changé
   dans un fichier déjà suivi.
2. Préparer le dossier du relecteur :

~~~sh
python3 .socle/socle review
~~~

   Il donne la consigne, le diff du lot depuis la branche distante (sinon
   la branche par défaut), les sujets que le lot ferme et les décisions
   qu'ils citent. `--base <ref>` change la base du lot.
3. Le confier à un relecteur sans contexte. Sous Claude Code : un
   sous-agent (outil `Agent`), du modèle de la session, dont le seul
   message est ce dossier, tel quel. Il n'a ni la conversation, ni la
   mémoire, ni l'état : ne rien y ajouter. Un agent sans sous-agents saute
   la revue, et son récap le dit.

## Les constats

Aucun ne bloque seul. Corriger chaque constat fondé, dans le lot, avant le
push ; répondre aux autres en une ligne : pourquoi il ne tient pas. Ne rien
poster sur GitHub : l'humain lit le récap, pas la revue.

Le récap le dit en une ligne : `Revue : <n> constats, <k> corrigés ;
écartés : <raison de chacun>`, ou `Revue : aucun constat`.
```

## Éléments cités

- ADR-0042@f52272e6 — la spécification de la revue adversariale, acceptée
  sur votre réponse à D-0072.
- D-0072@f60318f5 — la demande par laquelle vous avez validé cette
  spécification.
- B-0124@dfa9917f — le sujet de la revue adversariale, et ses deux critères
  de fin : la procédure écrite, et la mesure au banc.
- `test_l_installeur_les_pose_et_la_politique_les_protege` — le test qui
  vérifie que l'installeur pose les skills du socle et que la politique les
  protège ; il attend la liste `socle-private-memory`, `socle-request`, et
  attendra aussi `socle-review`.
- `test_dans_les_deux_langues_ils_passent_leurs_controles` — le test qui
  pose les skills en anglais et vérifie leurs contrôles ; il attend la même
  liste, dans le message de l'installeur.
- `.claude/skills/socle-review/SKILL.md` et `sha256:0ce646d6544049a5` — le
  fichier protégé nouveau de ce dépôt, et son empreinte.

## Où regarder

- [ADR-0042](https://github.com/theodubus/memory/blob/9d782ca8de35e19259df4c4f4f5e62567674fa56/memory/decisions/ADR-0042-la-revue-adversariale-d-un-lot-par-un-relecteur-sa.md) :
  la spécification, dont le skill suit la section « Décision ».
- [les deux tests](https://github.com/theodubus/memory/blob/9d782ca8de35e19259df4c4f4f5e62567674fa56/tests/test_skills.py#L120) :
  la liste attendue, qui gagnerait `socle-review`.
- Le skill, recopié dans le « Contexte » : vérifier qu'il dit quand faire
  la revue, comment la confier, et ce que fait l'agent de ses constats.

## Options

- **Valider** : l'agent commite le skill, son gabarit anglais, les deux
  tests, la ligne des instructions et la règle de ce dépôt ; effort nul
  pour vous ; risque faible, le skill ne s'applique qu'aux projets qui
  l'adoptent, et ce dépôt d'abord ; réversible.
- **Refuser** : rien ne se commite, et la revue reste sans procédure ;
  effort nul ; risque, la commande livrée ne sert pas ; réversible.

## Conséquences

Si vous validez, tout se commite dans la pull request en cours, ce dépôt
applique la revue à ses lots suivants, et l'agent passe à la mesure au
banc. Si vous refusez, le skill et les tests restent comme avant, et
l'agent revoit le skill avec vous. Sans réponse, rien ne se commite : le
skill attend dans l'arbre, et l'agent travaille sur autre chose.

## Recommandation

Valider. Vérifié : le skill passe ses contrôles (`skills.contrat`,
`skills.commandes`) en deux langues, et la suite des tests passe avec les
deux valeurs attendues nouvelles. Supposé : que ses consignes suffisent à
un agent pour mener la revue sans autre aide ; la mesure au banc le dira.

## Réponses possibles

- `valider` — le skill, ses deux tests, la ligne des instructions et la règle de ce dépôt se commitent.
- `refuser` — rien ne se commite ; l'agent revoit le skill.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
