<!-- socle: couche=demandes zone=publique -->
# D-0011 — Valider le changement des valeurs attendues de quatorze tests, que le renommage des chemins en anglais change

> date : 2026-10-11 · lu : decisions@50eefafa · bloque : le commit du renommage des chemins en anglais

## Décision demandée

Autoriser que quatorze tests du moteur attendent désormais les chemins
anglais du nouveau format de la mémoire (memory/, canonical.md,
private/, requests/, .answer.toml, guardrails.toml, engine.lock) au lieu des
chemins français, sans rien changer d'autre à ce qu'ils vérifient.

## Contexte

Tu m'as donné le feu vert pour renommer en anglais les dossiers et fichiers
que le socle pose dans un projet, quelle que soit la langue de la mémoire.
C'est fait, dans un travail pas encore commité : un projet neuf est posé
avec les chemins anglais, un projet existant garde les siens et se lit tel
quel, et la mise à jour le migre en renommant les fichiers, sans réécrire
la mémoire. La suite des tests passe, l'auto-test aussi.

Mais quatorze tests existants vérifient un chemin précis que le socle écrit
ou lit dans un projet jetable neuf, et ce chemin change de nom. Leur valeur
attendue doit donc changer. Depuis ta décision sur le point 2 de la
politique (une valeur attendue ne change que sur une demande validée, ou
une spécification écrite par toi ; une décision que j'écris ne suffit pas),
je ne peux pas les modifier seul : le contrôle des valeurs attendues refuse
le commit tant que tu n'as pas validé cette demande, qui nomme chaque test.
Pour onze d'entre eux, seul le nom de fichier attendu change ; pour deux
autres, la façon d'obtenir le chemin change (une constante supprimée est
remplacée par la table des chemins du format), et la valeur comparée ne
change pas. Aucun test n'est supprimé, aucune assertion n'est retirée ni
affaiblie.

## Éléments cités

- **Le renommage des chemins** : le sujet de backlog que tu as ouvert,
  « des noms de fichiers et de dossiers en anglais pour tous les projets ».
- **Le point 2 de la politique, tel que tu l'as tranché** : une valeur
  attendue ne change que sur une demande validée qui nomme le test, ou sur
  une spécification que toi seul as écrite.
- **Les quatorze tests**, avec l'avant et l'après de chaque assertion
  (le reste du test ne change pas) :

| Fichier | Test | Avant | Après |
| --- | --- | --- | --- |
| test_approbation.py | `test_rien_n_est_ecrit_pour_une_entree_ou_un_fichier_absents` | aucune approbation dans memoire/demandes | aucune approbation dans memory/requests |
| test_cli.py | `test_show_donne_l_empreinte` | en-tête `(memoire/backlog.md:4)` | en-tête `(memory/backlog.md:4)` |
| test_cli.py | `test_url_donne_le_permalien` | permaliens vers memoire/backlog.md et memoire/decisions/ | permaliens vers memory/backlog.md et memory/decisions/ |
| test_initialisation.py | `test_compagnon_sans_clone_le_dit` | .gitignore contient memoire/prive/ | .gitignore contient memory/private/ |
| test_initialisation.py | `test_chiffre_pose_le_filtre` | .gitattributes contient memoire/prive/** filter=git-crypt | .gitattributes contient memory/private/** filter=git-crypt |
| test_initialisation.py | `test_le_verrou_note_le_format` | le verrou lu par l'ancienne constante | le verrou lu par la table du format ; la valeur attendue, le numéro du format, ne change pas |
| test_installeur.py | `test_claude_md_garde_quand_le_projet_le_lit` | budget de CLAUDE.md dans .socle/garde-fous.toml | le même dans .socle/guardrails.toml |
| test_prive.py | `test_disponible_et_au_verrou` | memoire/prive/canonique.md | memory/private/canonical.md |
| test_prive.py | `test_changement_prive_hors_commit` | canonique.md | canonical.md |
| test_prive.py | `test_le_contenu_nouveau_est_prive_par_defaut` | l'entrée privée dans canonique.md, la publique dans memoire/canonique.md | dans canonical.md et memory/canonical.md |
| test_prive.py | `test_en_ci_un_constat_prive_est_masque` | le nom canonique.md n'apparaît pas | le nom canonical.md n'apparaît pas |
| test_prive.py | `test_sans_la_cle_la_memoire_est_indisponible` | memoire/prive/canonique.md illisible | memory/private/canonical.md illisible |
| test_prive.py | `test_liste_et_recherche` | les termes lus par l'ancienne constante | lus par la fonction qui donne le fichier des termes du projet ; la valeur attendue ne change pas |
| test_prive.py | `test_privees_sur_decision` | memoire/prive/demandes/*.reponse.toml protégé | memory/private/requests/*.answer.toml protégé |

## Où regarder

- [le sujet du renommage](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/memoire/backlog.md#b-0032--des-noms-de-fichiers-et-de-dossiers-en-anglais-pour-tous-les-projets) :
  vérifier que les noms anglais sont bien ceux que tu voulais.
- [la décision sur le point 2](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/memoire/decisions/ADR-0017-une-valeur-attendue-ne-change-que-sur-une-specific.md) :
  vérifier que c'est bien ce cas qu'elle couvre.
- Les tests dans leur version actuelle, pour comparer avec le tableau :
  [test_approbation.py](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/tests/test_approbation.py),
  [test_cli.py](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/tests/test_cli.py),
  [test_initialisation.py](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/tests/test_initialisation.py),
  [test_installeur.py](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/tests/test_installeur.py),
  [test_prive.py](https://github.com/theodubus/memory/blob/31a007967b29b4388e305318c3d0004a67efe0aa/tests/test_prive.py).
  La nouvelle version n'est pas poussée : le refus du contrôle empêche le
  commit. Le tableau ci-dessus en donne chaque assertion changée.

## Options

- **Valider** : les quatorze tests suivent les nouveaux chemins, et le
  renommage se commite. Effort nul de ton côté ; risque faible, puisque
  seul le nom du fichier vérifié change. Réversible : revenir aux chemins
  français ramène les anciennes valeurs.
- **Refuser** : le renommage ne se commite pas tel quel. Pour garder ces
  tests intacts, il faudrait qu'ils posent des projets à l'ancien format,
  et ils cesseraient de vérifier ce qu'un projet neuf reçoit ; ou renoncer
  au renommage.

## Conséquences

- Si tu valides : je consigne ta réponse, je commite le renommage avec la
  décision, le journal et les tests, et je pousse. Ce dépôt reste à
  l'ancien format jusqu'à ce que tu le migres toi-même (je te donnerai les
  trois commandes), car la migration renomme des fichiers protégés.
- Si tu refuses : le renommage reste non commité, et je te propose une autre
  voie ; je passe en attendant à la mémoire privée couche par couche.
- Sans réponse : le renommage attend, non commité ; je travaille sur les
  autres sujets que tu as approuvés, qui n'en dépendent pas tous.

## Recommandation

Valider. Vérifié : avec ces quatorze changements, toute la suite des tests
passe, l'auto-test aussi, et une répétition de la migration sur une copie
de ce dépôt ne laisse que les refus attendus (fichiers protégés renommés,
et ces valeurs attendues). Vérifié aussi : aucune assertion n'est retirée,
et deux des quatorze comparent la même valeur qu'avant. Supposé : aucun
autre projet n'est encore installé avec l'ancien format hors de ce dépôt et
de ses copies jetables.

## Réponses possibles

- `valider` — les quatorze tests suivent les nouveaux chemins ; le renommage se commite et se pousse.
- `refuser` — le renommage reste en attente, et je propose une autre voie.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
