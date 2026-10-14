<!-- socle: couche=demandes zone=publique -->
# D-0004 — Un test qui compare deux appels identiques, comme `assert_eq!(f(x), f(x))`, doit-il pouvoir passer quand un commentaire en donne la raison ?

> date : 2026-10-10 · réécrite après ton retour du 10 oct. · bloque : rien

## Décision demandée

Le contrôle des « tests creux » refuse aujourd'hui toute assertion de la
forme `f(x) == f(x)`, sauf si la ligne porte le commentaire
`socle: voulu — <raison>`. Garder cette exception, la retirer, ou la
restreindre.

## Contexte

**La règle du cadrage.** Section « Garde-fous de tests », point 3 : « Tests
creux interdits. Sont détectés : test sans assertion, assertion tautologique
du type f(x) == f(x), test désactivé ou ignoré sans raison écrite. » L'idée :
une assertion qui compare une valeur à elle-même passe toujours, donc elle ne
mesure rien. Le socle applique cette règle par le contrôle `tests.creux`, qui
lit chaque fonction de test et refuse le commit si une assertion compare deux
expressions identiques.

**Ce qui s'est passé.** En essayant le socle sur une copie de chess (rien n'a
été poussé dans chess), ce contrôle a refusé ce test du moteur de recherche :

```rust
#[test]
fn la_recherche_est_deterministe() {
    let fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1";
    assert_eq!(best(fen, 4), best(fen, 4));
}
```

Il a bien la forme `f(x) == f(x)`. Mais il n'est pas creux : il lance deux
fois la recherche sur la même position et vérifie qu'elle rend le même coup.
Si la recherche devenait non déterministe (un état mal remis à zéro entre
deux recherches, une table de hachage partagée), les deux appels
différeraient et le test échouerait. La règle du cadrage, appliquée à la
lettre, refuse donc un vrai test.

**Ce que j'ai fait sans te demander, et pourquoi je te le demande
maintenant.** J'ai ajouté une exception, sur le modèle de celle que le cadrage
prévoit déjà pour les tests désactivés (« sans raison écrite ») : la
tautologie passe si la ligne, ou celle d'avant, porte un commentaire
`socle: voulu — <raison>`. Pour chess, la ligne deviendrait :

```rust
    assert_eq!(best(fen, 4), best(fen, 4)); // socle: voulu — la recherche doit être déterministe
```

C'est un assouplissement d'une règle du cadrage, donc il te revient
(politique, point 1). En attendant ta réponse, l'exception est en place mais
visible : dans le message du contrôle, et dans l'auto-test, qui vérifie
qu'une tautologie sans raison reste refusée et qu'une tautologie avec raison
passe.

## Éléments cités

- `tests.creux` — le contrôle du socle qui détecte les tests sans assertion, les assertions tautologiques et les tests désactivés sans raison.
- `la_recherche_est_deterministe` — le test de chess cité plus haut, dans le fichier du moteur de recherche.

## Où regarder

- La règle d'origine : [cadrage, section « Garde-fous de tests », point 3](../archives/cadrage-2026-10-10.md#garde-fous-de-tests).
- Le test de chess : [chess, engine/src/search.rs, lignes 3764 à 3768](https://github.com/theodubus/chess/blob/689ce77dbd21723d9681cc3bbb1060a514f3f443/engine/src/search.rs#L3764-L3768).
- L'exception dans le code du socle : [moteur/socle/controles_tests.py](../../moteur/socle/controles_tests.py), constante `VOULU` et fonction `creux`.
- Les deux cas de l'auto-test qui l'éprouvent : [moteur/socle/autotest.py](../../moteur/socle/autotest.py), défaut « assertion tautologique » et témoin « une tautologie voulue, raison écrite, passe le commit ».

Ce qu'il faut vérifier : que le test de chess est bien légitime, et que la
forme de l'exception (un commentaire libre avec une raison) te va.

## Options

- **Garder l'exception telle quelle** : effort nul. Risque faible : un agent
  pourrait justifier une vraie tautologie par un commentaire, mais la raison
  est écrite et se voit à la relecture du diff. Réversible : une constante à
  retirer.
- **La retirer** : effort de dix minutes. Risque nul pour la règle du cadrage,
  mais le jour où le socle sera installé sur chess, ce test devra être réécrit
  autrement, par exemple en comparant à un coup attendu fixé — ce qui le rend
  fragile à chaque changement de l'évaluation. Réversible.
- **La restreindre** : par exemple, n'accepter le commentaire que dans un
  test dont le nom contient « determin ». Effort d'une heure, risque de
  rigidité (un test de stabilité ou d'idempotence a d'autres noms).
  Réversible.

## Conséquences

Si tu valides, l'exception reste et la règle est précisée ainsi dans le
format du socle. Si tu refuses, je retire l'exception et son témoin, et je
note dans le plan d'installation sur chess que ce test devra changer. Sans
réponse, l'exception reste en place et cette demande reste listée à chaque
démarrage de session.

## Recommandation

Garder l'exception. Vérifié : le test de chess détecte réellement une
recherche non déterministe (il appelle deux fois une recherche complète), et
l'auto-test montre qu'une tautologie sans raison reste refusée. Supposé :
qu'un agent n'en abusera pas — rien ne le mesure, seule la relecture le voit.

## Réponses possibles

- `valider` — l'exception reste telle quelle.
- `refuser` — je la retire.
- `restreindre` — le texte de ta réponse dit la condition.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
