<!-- socle: couche=backlog zone=publique -->
# B-0253 — Le hook de l'agent ne suit ni un return dans le corps d'une fonction, ni un appel indirect, ni une fonction nommée comme un builtin ou définie par un eval : la suppression du projet y passe

> statut : abandonné · origine : J-2026-11-16-B · priorité : haute · ref : J-2026-11-16-G · lu : backlog@0baae0e5

La seconde revue du lot L-0004 (J-2026-11-16-B) a trouvé des appels de
fonction que le découpage (`commands._analyser`, `fonctions`) ne suit pas,
avant le lot comme après, et où bash supprime le projet :

- un `return` dans le corps : `f() { cd memory; return; cd ..; }; f; rm
  -rf ../../<racine>` (aussi `[ -d x ] && return`, `if …; then return;
  fi`) ; seul le dossier de fin du corps compte ;
- un appel indirect : `f() { cd memory; }; fn=f; $fn; rm -rf
  ../../<racine>` ;
- une fonction nommée comme une commande que le hook lit déjà : `cd() {
  builtin cd memory; }; cd /tmp; rm -rf ../../<racine>` ;
- une fonction définie par un `eval` : `eval "f() { cd memory; }"; f; rm
  -rf ../../<racine>`.

Rares, mais rien ne rattrape la suppression du projet : un sujet, de
priorité haute (ADR-0080, sa première conséquence). La piste : un
`return` lu comme un `break` d'une boucle (les `sauts`) ; un appel par un
mot qui n'est pas connu en toutes lettres, vers une fonction retenue,
rend inconnu ce qu'elle change ; une fonction qui porte le nom d'un
builtin que le hook suit se juge comme une fonction.

Abandonné le 16 novembre selon D-0120 (J-2026-11-16-G) : un `return` dans une fonction, un appel indirect, une fonction nommée comme une commande ou définie par un `eval`, qu'aucun agent n'écrit dans son travail, va à la liste des formes connues que le hook ne juge pas (B-0261).

## Satisfait quand

- [ ] les quatre formes ci-dessus sont refusées par le hook, `f() { ls; return; }; f; rm -rf build` passe, et un test le montre
