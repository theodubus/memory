<!-- socle: couche=decisions zone=publique -->
# ADR-0022 — Un mois de journal continue dans un second fichier quand le premier atteint son budget

> statut : acceptée · date : 2026-10-12 · lu : decisions@e56960e0

## Contexte

Le journal tient un fichier par mois, en ajout seul, et chaque fichier a un
budget de taille (80 Ko par défaut). Ce dépôt a écrit plus de 80 Ko de
journal en douze jours d'octobre : le contrôle des budgets refusait alors
tout commit qui ajoutait une entrée, et le message conseillait d'archiver
« dans le journal », ce qui ne s'applique pas au journal lui-même. Un
fichier en ajout seul ne peut pas se vider ; relever le budget serait un
assouplissement, qui revient à l'humain, et ne ferait que repousser le cas.

## Décision

Quand une entrée ferait dépasser son budget au fichier du mois, le mois
continue dans un fichier suivant, `AAAA-MM-2.md`, puis `AAAA-MM-3.md`. Le
moteur choisit le fichier (`memoire.fichier_journal`) pour toutes ses
écritures au journal : une entrée nouvelle, une archive du backlog,
l'archive d'un cadrage. Une fois le mois continué, il n'écrit plus dans les
fichiers précédents. Le contrôle du format accepte déjà tout nom qui
commence par le mois de l'entrée ; aucun budget ne change.

## Conséquences

Chaque fichier reste borné, la recherche dans le journal (`grep -rn`) ne
change pas, et un identifiant reste unique sur tous les fichiers. Le
journal d'un mois peut s'étaler sur plusieurs fichiers. Pour défaire :
revenir au seul fichier par mois, en relevant le budget par une demande.
