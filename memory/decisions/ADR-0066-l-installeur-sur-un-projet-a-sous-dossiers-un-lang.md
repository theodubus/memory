<!-- socle: couche=decisions zone=publique -->
# ADR-0066 — L'installeur sur un projet à sous-dossiers : un langage sans manifeste à la racine, un adaptateur propre au projet, une marge au budget d'adoption

> statut : acceptée · date : 2026-11-11 · source : B-0168@98b2b15f, J-2026-11-11-S@5fc3364c, ADR-0052@1e39f204, ADR-0045@92db4f31 · lu : decisions@6c0be163

## Contexte

L'essai à blanc sur chess (B-0168@98b2b15f) : l'installeur a posé
l'adaptateur JavaScript parce que `ui/` porte un manifeste, et ses
commandes, lancées à la racine, échouent ; l'adaptateur préparé pour chess
ne pouvait pas lui être donné après coup, les hooks de l'agent, chargés dès
l'écriture des réglages, refusant de l'écrire ; le budget du fichier
d'instructions a été posé à 66 octets de sa taille. Décisions réversibles
et mesurables (politique, point 3).

## Décision

1. *Un langage sans manifeste à la racine.* En automatique, un langage
   dont tous les manifestes sont dans des sous-dossiers ne reçoit pas
   d'adaptateur ; l'installeur le dit (`!!`), avec ses manifestes et deux
   issues : un adaptateur propre au projet, dont les commandes entrent dans
   le sous-dossier, ou le sous-dossier déclaré tiers (`[thirdparty] paths`),
   une décision de l'humain. Un manifeste à la racine garde le comportement
   d'avant, et compte aussi ce qui lance l'outil de la racine (revue du
   lot) : pour Gradle, `gradlew`, `settings.gradle` ou `build.gradle` ;
   pour Python, pytest, qui parcourt les sous-dossiers, ou un dossier
   `tests/` à la racine, que lit `unittest discover -s tests`. Les langages
   des adaptateurs déjà posés comptent pour couverts, et un fichier
   d'adaptateur écarté par un principal du même langage en place est dit
   non posé. Le principal se déduisait déjà de la racine seule.
2. *Un adaptateur propre au projet.* `--adapter` prend le chemin d'un
   `.toml` ; il est jugé par le contrat des adaptateurs (chaque capacité, la
   lecture des tests : `ecarts_au_contrat`, qu'`adaptateur.capacites` lit
   aussi), et l'installeur refuse (code 2) un fichier qui ne le tient pas,
   avant d'écrire quoi que ce soit. Posé, il est une copie que le projet a
   adaptée : la mise à jour le garde (ADR-0052@1e39f204, point 3).
3. *La marge du budget d'adoption.* Le budget qu'une adoption fixe à un
   fichier est sa taille plus un dixième, arrondie au millier supérieur ;
   l'installeur dit la taille et la règle. Il ne se fixe qu'aux fichiers qui
   dépassent leur budget, ou au `CLAUDE.md` gardé comme source, comme
   avant. Le cliquet ne le laisse ensuite que baisser, et une mise à jour
   qui le dépasse se dit comme avant (ADR-0045@92db4f31).

## Conséquences

Chess s'installera avec `--adapter` sur son adaptateur Rust, et l'interface
sous `ui/` sera déclarée tierce ou équipée de son propre adaptateur.
Lancer un adaptateur maintenu dans un sous-dossier est B-0174@f2792822. Ce qui reste
supposé : qu'un dixième suffise entre deux resserrements d'un fichier
d'instructions. La défaire : `langages_en_sous_dossier` et
`budget_d_adoption` de l'installeur, et leurs tests dans
`tests/test_installeur.py`.
