<!-- socle: couche=backlog zone=publique -->
# B-0370 — Une demande qui assouplit un garde-fou ou change une valeur attendue sans nommer la clé ni le test ne couvre rien une fois validée : l'humain répond deux fois

> statut : ouvert · origine : J-2026-11-26-BA · ref : D-0220, D-0221, T-0205 · lu : backlog@c0fe16c8

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

## Satisfait quand

- [ ] une demande qui dit assouplir un garde-fou ou changer une valeur attendue, sans nommer une clé des garde-fous ni une fonction de test, est signalée avant d'être poussée, avec ce qu'il faudrait citer
- [ ] une demande qui les nomme passe sans signal
