<!-- socle: couche=demandes zone=publique -->
# D-0021 — Choisir ce que les noms anglais renomment dans le socle

> date : 2026-10-13 · lu : decisions@a1a1eb4f

## Décision demandée

Choisir ce que le renommage en anglais touche dans le socle : tout ce qui
est du code, ou seulement ce qu'on tape et les noms de fichiers et de
dossiers.

## Contexte

Tu as signalé que des noms de fichiers et de dossiers du socle sont encore
en français, et validé qu'ils passent en anglais avec le backlog en un
fichier par sujet. L'inventaire, fait avant de commencer, montre deux
choses. D'abord, rien de ce qui reste en français n'est versionné dans un
projet installé : sa mémoire et sa configuration sont déjà en anglais,
et le moteur s'y remplace en bloc. Il n'y aura donc pas de migration de
projet pour ces noms. Ensuite, l'écart est bien plus large que les
fichiers : la décision qui fixe les langues veut en anglais les
identifiants Python publics, et le moteur en a 359, presque tous en
français, dans 33 modules aux noms français. Les renommer tous touche
toute la suite de tests, dont au moins 228 lignes d'assertion qui nomment
un module, et chaque assertion changée demande ta validation.

## Éléments cités

- **Le sujet des noms encore en français** (B-0045@b5c00d64) : ton
  signalement, et la liste de départ (dossiers, modules, gabarits,
  commandes et options).
- **La décision sur les langues** (ADR-0002@5b36d00d) : le contenu en
  français ; en anglais, les noms de commandes, les clés de configuration
  et les identifiants Python publics.
- **L'inventaire** : les dossiers `moteur/`, `modeles/`, `adaptateurs/`,
  `banc/` ; 33 modules (`controles_memoire.py`, `prive.py`,
  `memoire.py`…) et 359 fonctions et classes publiques ; 16 gabarits
  (`garde-fous.toml`, `politique.toml`, `demande.md`, `memoire/…`) ; les
  commandes `aide`, `prive` (et ses actions `etat`, `installer`,
  `verrouiller`, `extraire`, `recuperer`, `terme`, `basculer`) et `relu` ;
  les options `--court`, `--poser`, `--oui`, `--cadrage`, `--depot`,
  `--refaire` (`--rapide` a déjà son nom anglais, `--fast`).
- **Le dossier du moteur de ce dépôt** : son nom, `moteur/`, est écrit dans
  le verrou du moteur, un fichier protégé que seul toi modifies.

## Où regarder

- [le sujet des noms en français](https://github.com/theodubus/memory/blob/f2cca13040722f330f03ce6a78575e81b880ef1d/memory/backlog/B-0045-des-noms-de-fichiers-et-de-dossiers-sont-encore-en.md) :
  ce que tu as signalé.
- [la décision sur les langues](https://github.com/theodubus/memory/blob/f2cca13040722f330f03ce6a78575e81b880ef1d/memory/decisions/ADR-0002-langue-francais-identifiants-anglais.md) :
  vérifier qu'elle veut bien les identifiants Python publics en anglais.
- [la ligne de commande](https://github.com/theodubus/memory/blob/f2cca13040722f330f03ce6a78575e81b880ef1d/moteur/socle/cli.py) : les noms des
  commandes et des options, en bas du fichier.

## Options

- **Tout** : dossiers, modules, gabarits, identifiants publics, commandes
  et options ; les anciens noms de commandes gardés le temps d'une
  version. Effort très important, plusieurs sessions ; toute la suite de
  tests touchée, et ta validation de ses assertions changées ; risque
  moyen, un renommage oublié casse un appel que les tests ne couvrent pas ;
  réversible par un renommage inverse.
- **Ce qu'on tape et les noms de fichiers** : commandes et options (avec
  leurs anciens noms le temps d'une version), dossiers, gabarits et noms
  des modules ; les fonctions gardent leurs noms français, et la décision
  sur les langues est corrigée en ce sens. Effort moyen ; les assertions
  qui nomment un module changent aussi, donc ta validation ; risque faible,
  les anciens noms de commandes restant valides une version ; réversible.
- **Les commandes et les options seulement**, avec leurs anciens noms le
  temps d'une version. Effort faible ; aucune assertion ne change ; risque
  faible ; réversible ; les noms de fichiers restent en français.
- **Rien** : corriger la décision sur les langues pour dire que le code du
  moteur reste en français. Effort nul ; aucun risque ; réversible.

## Conséquences

- Si tu valides tout, ou ce qu'on tape et les fichiers : j'écris la liste
  des renommages, puis une demande qui nomme les tests dont les assertions
  changent, avant de les committer ; tu renommes le dossier du moteur dans
  le verrou de ce dépôt, ou tu relances l'installeur.
- Si tu valides les commandes seulement : je le fais sans autre demande.
- Si tu refuses tout renommage (rien) : j'écris la décision qui corrige
  celle sur les langues, et le sujet se clôt.
- Sans réponse : rien ne change ; le sujet reste ouvert.

## Recommandation

Ce qu'on tape et les noms de fichiers : c'est ce que tu as signalé, et ce
que l'humain et l'agent voient ; renommer les 359 fonctions coûterait
plusieurs sessions et toucherait toute la suite pour un gain que personne
ne voit. Vérifié : l'inventaire, et qu'aucun de ces noms n'est versionné
dans un projet installé. Supposé : l'effort, estimé sans l'avoir fait.

## Réponses possibles

- `tout` — tout ce qui est du code passe en anglais, fonctions comprises.
- `fichiers` — commandes, options, dossiers, gabarits et modules ; les fonctions restent en français.
- `commandes` — les commandes et les options seulement.
- `rien` — la décision sur les langues est corrigée ; rien n'est renommé.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
