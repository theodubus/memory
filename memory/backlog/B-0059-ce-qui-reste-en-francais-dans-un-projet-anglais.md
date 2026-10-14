<!-- socle: couche=backlog zone=publique -->
# B-0059 — Ce qui reste en français dans un projet anglais

> statut : ouvert · origine : J-2026-10-14-N · lu : backlog@c4743d32

Suite de B-0038 : le moteur parle la langue du projet, mais un projet
anglais lit encore du français à six endroits, hors du moteur ou à la
marge :

- les textes `absent` et `replacement` des adaptateurs, écrits dans
  leurs fichiers (`engine/socle/adapters/*.toml`), que `verify` affiche ;
- les noms du travail et des étapes des workflows de CI ; le nom du
  travail est aussi celui que la protection de la branche exige, le
  changer touche les projets déjà protégés ;
- le marqueur des valeurs liées, `<!-- valeur:nom -->`, que seul le
  français fait reconnaître ;
- les descriptions des défauts et des témoins de l'auto-test ;
- le statut d'une demande que `socle show` affiche (« en attente »,
  « répondue : … »), une valeur interne aussi comparée ailleurs ;
- le message du lanceur sous un Python trop ancien, écrit avant que le
  moteur ne se charge.
