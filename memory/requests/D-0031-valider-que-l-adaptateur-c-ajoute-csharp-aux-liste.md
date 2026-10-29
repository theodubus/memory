<!-- socle: couche=demandes zone=publique -->
# D-0031 — Valider que l'adaptateur C# ajoute « csharp » aux listes de deux tests

> date : 2026-10-20 · lu : decisions@71682948

## Décision demandée

Valider que l'écriture de l'adaptateur C# change la valeur attendue de deux
tests, qui fixent la liste exacte des adaptateurs maintenus et celle des
projets du banc des adaptateurs, en y ajoutant « csharp ».

## Contexte

Tu m'as laissé travailler en autonomie sur le backlog, sans arbitrage.
Le sujet de l'adaptateur C# (dotnet test pour les tests, Stryker.NET pour
la mutation) attendait un endroit où dotnet existe. Je viens de mesurer
qu'il existe ici : le téléchargement officiel de .NET est refusé par la
politique réseau du conteneur, mais le SDK .NET 8 s'installe par le paquet
d'Ubuntu, et NuGet répond. Sur un projet jetable (une solution, une
bibliothèque, ses tests xUnit), les tests passent, le formateur de .NET
tourne, et Stryker.NET 4.16.0 (la 5.0.0 exige un .NET plus récent) écrit
un rapport au même schéma que celui que le socle lit déjà pour JavaScript,
à deux écarts près : le nom du fichier et des chemins absolus. L'action
GitHub qui installe .NET existe dans une version qui tourne sur Node 24.

L'adaptateur est donc faisable, mais pas sans toi : deux tests existants
comparent la liste des adaptateurs à une valeur écrite en dur. Le premier,
`test_les_adaptateurs_maintenus`, attend exactement go, java, javascript,
php, python, python-pytest, ruby et rust ; le second,
`test_un_projet_par_adaptateur_nouveau`, attend exactement les projets du
banc go, java, javascript, php et ruby. Ajouter C# ajoute « csharp » à ces
deux listes. La politique (point 2) interdit de changer une valeur
attendue sans une demande validée qui nomme le test. Rien n'est écrit ;
j'attends ta réponse avant de coder.

Ce que contiendrait le travail, si tu valides : l'adaptateur (`dotnet
build`, `dotnet test`, `dotnet format`, Stryker.NET épinglé dans le
manifeste d'outils du projet, la lecture des tests xUnit, NUnit et MSTest,
leurs assertions, leurs tests désactivés et leurs valeurs attendues) ; le
lecteur des rapports de Stryker étendu à celui de Stryker.NET ; la
détection d'un projet C# par sa solution ou ses fichiers de projet ;
l'étape de CI qui installe .NET ; et un projet jetable au banc des
adaptateurs, éprouvé ici sur ses douze étapes, comme les cinq derniers.

## Éléments cités

- B-0040@535fd104 — le sujet du backlog : un adaptateur C#, à éprouver là
  où dotnet existe.
- ADR-0021@d84f5620 — la décision des cinq adaptateurs précédents, chacun
  avec l'outil de tests et de mutation le plus courant de son langage.
- J-2026-10-20-L@cf4cbd30 — l'entrée du journal qui consigne les mesures faites ici
  sur .NET et Stryker.NET.

## Où regarder

- [le premier test](https://github.com/theodubus/memory/blob/4db7721cac15784cbbc72cfe94756bfef2317c30/tests/test_adaptateurs.py#L22-L24) :
  la liste des adaptateurs maintenus, où « csharp » s'ajouterait.
- [le second test](https://github.com/theodubus/memory/blob/4db7721cac15784cbbc72cfe94756bfef2317c30/tests/test_banc_adaptateurs.py#L24-L25) :
  la liste des projets du banc, où « csharp » s'ajouterait.
- [le sujet de l'adaptateur C#](https://github.com/theodubus/memory/blob/4db7721cac15784cbbc72cfe94756bfef2317c30/memory/backlog/B-0040-un-adaptateur-c-dotnet-test-stryker-net-a-eprouver.md) :
  ce que tu voulais quand tu l'as demandé.

À vérifier : que ces deux changements se bornent à ajouter « csharp », et
que tu veux bien l'adaptateur C# maintenant.

## Options

- **Valider** : j'écris l'adaptateur, ses tests, et ajoute « csharp » aux
  deux listes ; je le passe au banc des adaptateurs ici, puis je pousse.
  Effort : quelques heures. Risque faible : les deux listes ne changent
  que d'un nom ; un adaptateur de plus est un adaptateur à maintenir.
  Réversible : un commit qui se défait.
- **Refuser** : rien n'est écrit ; le sujet reste ouvert, avec les mesures
  au journal pour plus tard. Effort nul ; aucun risque ; pas de C#.

## Conséquences

- Si tu valides : j'écris et j'éprouve l'adaptateur, je consigne ta
  réponse, je pousse, et je te donne le lien du résultat du banc.
- Si tu refuses : rien ne change, et le sujet garde ses mesures.
- Sans réponse : rien n'est écrit ; le sujet attend, et je ne touche pas
  aux deux tests.

## Recommandation

Valider. Vérifié : .NET 8 s'installe ici par le paquet d'Ubuntu ; les
tests, le formateur et Stryker.NET 4.16.0 tournent sur un projet
jetable ; son rapport suit le schéma déjà lu pour JavaScript ; l'action
qui installe .NET dans la CI tourne sur Node 24. Supposé : que les douze
étapes du banc passent pour C# comme pour les cinq derniers langages, ce
que le banc dira.

## Réponses possibles

- `valider` — j'écris l'adaptateur C# et ajoute « csharp » aux listes des deux tests.
- `refuser` — rien n'est écrit ; le sujet reste ouvert.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
