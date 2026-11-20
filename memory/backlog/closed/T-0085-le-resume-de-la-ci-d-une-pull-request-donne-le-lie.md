<!-- socle: couche=backlog zone=publique -->
# T-0085 — Le résumé de la CI d'une pull request donne le lien des demandes posées sur sa branche, pas seulement celles de la branche par défaut

> statut : fait · origine : J-2026-11-18-L · ref : J-2026-11-20-AI · besoin : B-0274 · lu : backlog@d0ff4815

Relevé par la revue de L-0014, passe 1 (J-2026-11-18-L), constat 3 pour
le backlog. Le résumé que la CI posée écrit à chaque exécution (`socle
roadmap --format markdown`, T-0058) donne le lien de chaque demande en
attente par `links.lien`, qui vise le commit poussé (`commit_pousse`,
`engine/socle/links.py`, vers la ligne 80). Sur une pull request, la CI
tourne sur une HEAD détachée, le commit de fusion : `commit_pousse` rend
`origin/main`, et une demande posée sur la branche, le cas courant, n'a
pas de lien. Le livrable, un commit : sur la HEAD détachée d'une pull
request, le lien vise le commit de tête de la pull request.

## Fait quand

- [x] sur la HEAD détachée d'une pull request, le résumé donne le lien d'une demande posée sur sa branche, et un test le montre
