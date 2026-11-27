<!-- socle: couche=backlog zone=publique -->
# B-0370 — Une demande qui assouplit un garde-fou ou change une valeur attendue sans nommer la clé ni le test ne couvre rien une fois validée : l'humain répond deux fois

> statut : ouvert · origine : J-2026-11-26-BA · ref : D-0220, D-0221, T-0205, D-0234, D-0235 · après : B-0375 · lu : backlog@c0fe16c8

Vu le 26 novembre (J-2026-11-26-BA) : D-0220, validée par Théo, devait
couvrir le relèvement du plafond de `memory/directives.md` et la valeur
attendue de son test. Elle ne citait que le fichier des garde-fous et un
lien vers la ligne du test : `cliquet.garde-fous` attend une demande
validée dont le texte contient la clé
(`budgets."memory/directives.md".max_bytes`), et `tests.attendus` une
qui nomme la fonction de test. La validation ne couvrait rien ; il a
fallu reposer la question, D-0221, qui nommait la clé et le test, et
Théo a répondu deux fois à la même décision.

Le contrat des demandes le dit déjà (« Seule `valider` autorise à
changer un test ou une clé des seuils que la demande nomme ») et
`requests.gestes_nommes` sait ce qu'une demande nomme, mais rien ne le
signale à l'écriture d'une demande, avant qu'elle parte vers l'humain.

Arbitré par Théo le 27 novembre (D-0235, point 9, J-2026-11-27-U) : vu
une fois, rare et bénin, il ne vaut qu'une ligne, celle du contrat que
`socle new request` imprime à l'écriture d'une demande, au moment où elle
sert ; le signal avant le push s'écarte. Ses critères sont récrits ainsi.

## Satisfait quand

- [ ] le contrat que `socle new request` imprime dit, en une ligne, qu'une demande qui assouplit un garde-fou ou change une valeur attendue nomme la clé des garde-fous ou la fonction de test qu'elle couvre
