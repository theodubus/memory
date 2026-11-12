<!-- socle: couche=backlog zone=publique -->
# B-0189 — Seconde revue de B-0180 : un fichier renommé perd sa tolérance à la pull request suivante, et la clé ne dit plus le genre de faute

> statut : fait · origine : J-2026-11-12-D · priorité : haute · lu : backlog@d439d914 · ref : J-2026-11-12-E

Les corrections de la première revue de B-0180 étaient lourdes (la clé
d'un constat refaite, `trad` qui rend un texte gardant sa source) : la
session les a fait relire une seconde fois avant de fusionner. Le risque
sur `trad` est écarté ; six constats restent, sur le lot déjà poussé :

1. Un fichier renommé ne garde sa tolérance que dans la pull request qui
   le renomme : la liste garde l'ancien nom, rien ne dit de la mettre à
   jour, la pull request suivante échoue, et réparer la liste y exige une
   demande validée. Le guide promet le contraire.
2. À la mise à jour d'un projet adopté avant la règle, un fichier renommé
   sur la branche perd ses constats anciens.
3. La clé ne dit plus le genre de faute : un lien mort corrigé et un
   chemin cité inexistant vers la même cible ont la même clé, et le second
   passe à la place du premier.
4. L'avertissement « résorbé » cite le nouveau nom d'un fichier renommé,
   que la liste ne contient pas.
5. Deux messages d'erreur perdent leur source française (une f-string, une
   concaténation) : leur clé dépend alors de la langue.
6. Une clé dont le chemin contient un tiret long n'est pas suivie.

## Fait quand

- [x] renommer un fichier qui porte un constat toléré se règle dans la pull request qui le renomme : le contrôle demande de renommer la clé dans la liste, ce que le cliquet laisse faire, et le guide le dit
- [x] la mise à jour d'un projet adopté avant la règle suit les renommages de la branche
- [x] deux fautes de genre différent sur la même cible ont deux clés, sans changer les clés déjà consignées par un test poussé
- [x] les constats 4, 5 et 6 sont corrigés, chacun avec un test
