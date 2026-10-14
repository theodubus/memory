<!-- socle: couche=demandes zone=publique -->
# D-0022 — Valider quatre assertions de tests qui nomment une commande ou une option renommée

> date : 2026-10-13 · lu : decisions@efc2a4a3

## Décision demandée

Valider que quatre tests changent la commande ou l'option qu'ils
attendent, de son ancien nom français à son nouveau nom anglais, et qu'un
cinquième change la liste des dossiers qu'il parcourt.

## Contexte

Tu as choisi que ce qu'on tape et les noms de fichiers du socle passent en
anglais, les fonctions gardant leurs noms français. C'est fait dans l'arbre
de travail, pas encore commité : les commandes `aide`, `prive` et `relu`
deviennent `help`, `private` et `reviewed` ; les actions de `private`
deviennent `status`, `install`, `lock`, `extract`, `recover`, `term` et
`move` ; les options `--oui`, `--cadrage`, `--depot`, `--poser` et
`--court` deviennent `--yes`, `--brief`, `--repo`, `--record` et
`--short`. Les anciens noms restent acceptés une version, et le hook
refuse une commande réservée à l'humain sous ses deux noms. Les dossiers
du moteur, ses modules et ses gabarits sont renommés aussi.

Les messages du moteur donnent désormais les nouveaux noms : quatre tests,
qui vérifiaient un message ou une commande sous l'ancien nom, doivent
attendre le nouveau. Changer ce qu'un test attend exige ta validation ; je
ne les commite pas avant ta réponse, et le reste du travail attend avec
eux, parce que sans eux la suite échoue.

Les quatre assertions, avant → après :

1. Le refus d'approuver sans confirmation, dans
   `test_sans_liste_ni_confirmation_rien_n_est_approuve` : le message
   contient `--oui` → `--yes`.
2. Le workflow de mutation posé par l'installeur, dans
   `test_le_workflow_et_sa_ligne_quand_l_adaptateur_balaie` : il contient
   `python3 .socle/socle mutation-run --poser` → `--record`.
3. Les étapes que l'installation donne à l'humain, dans
   `test_l_installation_dit_quoi_faire_ensuite` : la première contient
   `socle init --cadrage` → `socle init --brief`.
4. Le verrou de la mémoire privée, dans
   `test_commande_verrouiller_puis_extraire` : la commande est appelée
   avec l'action `verrouiller` puis `extraire` → `lock` puis `extract` ;
   la valeur attendue, le code de sortie 0, ne change pas.

Et une valeur hors des assertions : le test qui vérifie que les chemins
cités dans les docstrings du moteur existent,
`test_un_chemin_du_depot_cite_existe`, parcourt les dossiers `docs`,
`moteur`, `tests`, `banc` → `docs`, `engine`, `tests`, `bench`. Sans ce
changement, il ne regarderait plus les chemins du moteur sous leur nouveau
nom.

## Éléments cités

- **Ton choix sur les noms anglais** (D-0021@90ac5e5d) : ce qu'on tape et
  les noms de fichiers, les fonctions restant en français.
- **La décision qui l'applique** (ADR-0027@a8288770) : les noms retenus, les
  anciens noms acceptés une version, et les contrôles qui suivent un
  renommage.
- **Le sujet des noms en français** (B-0045@b5c00d64) : ton signalement.

## Où regarder

- [la décision qui applique ton choix](https://github.com/theodubus/memory/blob/18f5c950e8db6e0328061dc1eb6e777d922c4acd/memory/decisions/ADR-0027-les-noms-de-fichiers-et-les-commandes-du-socle-en.md) :
  vérifier les noms retenus.
- [le test de l'approbation](https://github.com/theodubus/memory/blob/a53eeeafaa3f831218c7fd20f583316ad2e7cf55/tests/test_approbation.py#L119-L125),
  [celui du workflow de mutation](https://github.com/theodubus/memory/blob/a53eeeafaa3f831218c7fd20f583316ad2e7cf55/tests/test_balayage.py#L300-L306),
  [celui de l'installation](https://github.com/theodubus/memory/blob/a53eeeafaa3f831218c7fd20f583316ad2e7cf55/tests/test_initialisation.py#L102-L109),
  [celui du verrou privé](https://github.com/theodubus/memory/blob/a53eeeafaa3f831218c7fd20f583316ad2e7cf55/tests/test_prive.py#L170-L180)
  et [celui des docstrings](https://github.com/theodubus/memory/blob/a53eeeafaa3f831218c7fd20f583316ad2e7cf55/tests/test_moteur.py#L47-L63) :
  chaque assertion sous son ancien nom ; seul le nom change.

## Options

- **Valider** : les cinq tests attendent les nouveaux noms, et le travail
  se commite. Effort nul de ton côté ; risque faible, chaque test garde
  ce qu'il vérifie ; réversible par un commit inverse.
- **Refuser** : les commandes et options gardent leurs noms français, le
  reste du renommage (dossiers, modules, gabarits) se commite seul. Effort
  faible ; risque faible ; réversible ; ton choix de D-0021 n'est alors
  appliqué qu'en partie.

## Conséquences

- Si tu valides : je commite les tests et le renommage, puis je pousse ;
  il te restera deux fichiers protégés à mettre à jour (le verrou de ce
  dépôt et sa CI), que je décris dans un sujet du backlog à ton nom.
- Si tu refuses : je rends leurs noms français aux commandes et aux
  options, et je commite le reste.
- Sans réponse : rien n'est commité ; le travail attend dans l'arbre.

## Recommandation

Valider. Vérifié : la suite complète passe avec ces cinq changements, et
chaque test garde ce qu'il vérifie, sous le nouveau nom. Supposé : rien.

## Réponses possibles

- `valider` — les cinq tests attendent les nouveaux noms.
- `refuser` — les commandes et les options gardent leurs noms français.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
