<!-- socle: couche=demandes zone=publique -->
# D-0032 — Pousser le projet C# jetable dans le dépôt d'essai pour y faire tourner sa CI et son balayage

> date : 2026-10-20 · lu : decisions@71682948

## Décision demandée

Valider que je pousse le projet C# jetable du banc des adaptateurs sur une
branche `csharp` de ton dépôt d'essai public `theodubus/tests`, pour y
voir tourner la CI et le balayage de mutation que le socle pose dans un
projet C#.

## Contexte

L'adaptateur C# est écrit et passe les douze étapes de son banc, mais dans
ce conteneur seulement. Les étapes qu'il ajoute à la CI du projet n'ont
jamais tourné sur GitHub : installer .NET par `actions/setup-dotnet@v5`
(les SDK 8 et 10), puis `dotnet restore && dotnet tool restore`. Le choix
des deux SDK est supposé : le SDK 10 construit, et les tests d'un projet
qui cible .NET 8 trouvent leur environnement d'exécution ; si c'est faux,
un projet C# qui installe le socle a une CI rouge dès son premier push.

Tu as répondu « Ok pour la CI de C# » à ma proposition ; c'est une
publication, donc elle passe par cette demande, que tu as pu lire.

Ce serait le même essai que pour les cinq autres langages, le 15 octobre :
une branche par langage dans `theodubus/tests`, la CI lue à chaque push,
le balayage lancé à la main (il est déjà enregistré par GitHub dans ce
dépôt). Le projet contient le moteur du socle, comme les cinq autres, ce
que tu avais accepté (« publier »). Le dépôt se clone hors du dossier des
dépôts de ma session, sans en devenir la racine, comme tu l'avais
demandé.

## Éléments cités

- B-0040@fae2ac6a — le sujet de l'adaptateur C#, fait : écrit et éprouvé
  au banc dans ce conteneur.
- F-0025@4a740694 — le fait mesuré : 12 étapes sur 12 au banc, ici, pas
  sur GitHub.
- D-0025@ae4cfd76 — la demande du premier essai sur GitHub, pour les cinq
  autres langages, validée `public` dans `theodubus/tests`.
- D-0027@42e04c4d — ta réponse `publier` : le moteur du socle peut être
  publié dans ce dépôt public.
- J-2026-10-14-S@bdeb6162 — tes précautions pour travailler avec un autre
  dépôt : le cloner à part, sans en faire la racine de la session.
- J-2026-10-15-K@621ba792 — comment le balayage a tourné sur GitHub pour
  les cinq langages : lancé à la main, sur chaque branche.

## Où regarder

- [les étapes de CI de l'adaptateur C#](https://github.com/theodubus/memory/blob/b101009b1192c854dc54b443a49f169b6e329d93/engine/socle/adapters/csharp.toml#L19-L30) :
  ce qui n'a jamais tourné sur GitHub.
- [le banc de l'adaptateur C#](https://github.com/theodubus/memory/blob/b101009b1192c854dc54b443a49f169b6e329d93/memory/journal/2026-10-3.md#j-2026-10-20-n--b-0040--ladaptateur-c-passe-les-douze-%C3%A9tapes-du-banc) :
  ce qui est mesuré ici.

À vérifier : que tu acceptes une branche de plus dans `theodubus/tests`
(il existe toujours, public, et ma session peut y pousser : lu le 20 oct.).

## Options

- **Valider** : j'ajoute `theodubus/tests` à ma session, j'y pousse le
  projet sur la branche `csharp`, je lis sa CI, je lance le balayage, et je
  corrige l'adaptateur si une étape échoue. Effort pour toi : nul, sauf
  confirmer l'ajout du dépôt si ta session le demande. Risque faible : un
  petit module de calcul, ses tests et le moteur, déjà publié là ; les
  minutes de CI d'un dépôt public sont gratuites. Réversible : supprimer la
  branche efface tout.
- **Refuser** : rien n'est poussé ; les étapes de CI de C# restent
  supposées. Effort nul ; risque moyen : une CI rouge au premier push d'un
  projet C# ; réversible.

## Conséquences

- Si tu valides : je fais l'essai dans ce tour-là, je te donne les liens
  des exécutions, et l'adaptateur est corrigé si besoin.
- Si tu refuses : rien ne change ; le fait F-0025 garde sa réserve « pas
  sur GitHub ».
- Sans réponse : rien n'est poussé, et je ne touche pas au dépôt d'essai.

## Recommandation

Valider. Vérifié : l'adaptateur passe son banc ici ; `actions/setup-dotnet@v5`
tourne sur Node 24 (lu dans son fichier d'action) ; le même essai a marché
pour les cinq autres langages. Supposé : que le SDK 10, installé à côté du
8, construise et teste un projet qui cible .NET 8, et que Stryker.NET 4.16.0
tourne sous lui.

## Réponses possibles

- `valider` — je pousse le projet C# sur la branche `csharp` du dépôt d'essai et je lis sa CI et son balayage.
- `refuser` — rien n'est poussé ; les étapes de CI de C# restent supposées.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
