<!-- socle: couche=backlog zone=publique -->
# B-0080 — Un clone sans la branche par défaut prend sa propre branche pour elle, et le hook refuse son push

> statut : fait · origine : J-2026-10-20-U · ref : J-2026-10-22-C · lu : backlog@412062c4

Mesuré le 20 oct., dans une session neuve : le clone n'avait que la branche
de travail ; `utils.branche_par_defaut` ne trouve ni `origin/HEAD`, ni
`origin/main`, ni `main`, et retombe sur la branche amont de la branche
courante, c'est-à-dire elle-même. Le hook de l'agent refuse alors tout push
comme un « push sur la branche par défaut », et la base de travail devient
la branche poussée. `git fetch origin main` règle le cas. Le repli sur
l'amont sert un dépôt neuf qui n'a que sa branche de travail ; il ne
devrait pas faire de la branche courante la branche par défaut quand le
dépôt distant en a une autre (`git ls-remote --symref origin HEAD` le dit),
ou le refus devrait le dire et conseiller le `fetch`.
