<!-- socle: couche=demandes zone=publique -->
# D-0042 — Choisir la conception des skills : ceux que pose le socle, ceux qu'écrit l'agent, et leurs contrôles (B-0066)

> date : 2026-10-22 · lu : decisions@2a93e7ab

## Décision demandée

Choisir comment le socle se sert des skills : lesquels il pose lui-même,
quand l'agent en écrit pour le projet, et ce que les contrôles en
vérifient.

## Contexte

Théo a demandé que l'agent ajoute des skills de lui-même quand c'est
nécessaire. Un skill est une procédure rangée dans un dossier, avec un
fichier `SKILL.md` dont l'en-tête donne un nom et une description ; l'agent
ne le charge que lorsque sa description correspond à la tâche, au lieu de
relire la procédure à chaque session.

Ce qui a été mesuré ou lu pour cette étude :

- **Les instructions de l'agent.** La section du socle dans `AGENTS.md`
  pèse 11,4 Ko et se relit en entier à chaque démarrage. Trois parties
  servent rarement : poser une demande et relayer une réponse (1,5 Ko), la
  mémoire privée (environ 1 Ko), le tableau de ce qui tourne tout seul
  (0,9 Ko).
- **BMAD n'ajoute pas de skills de lui-même**, ce qui répond à la question
  de Théo. Dans BMAD Method 6.12.4, la version que pose le socle, aucun
  workflow n'écrit de skill ; la rétrospective propose des actions et n'en
  applique aucune. Un module officiel à part, BMad Builder (1.1.0), que le
  socle n'installe pas, fabrique des skills sur demande : « build a
  workflow », « optimize skill ». Il procède par une conversation en six
  phases, a un mode sans interaction, un lint déterministe (conventions de
  chemins, structure) et des relectures par sous-agents. Il écrit dans
  `_bmad-output/skills`, où l'agent ne charge rien, et suit les
  conventions de BMAD (sa configuration dans `_bmad`). Un module tiers,
  d'un autre auteur, tire des skills du code et de la documentation ; il
  n'a pas été examiné plus avant.
- **Ce que le socle fait déjà.** Les skills de BMAD sont déclarés fichiers
  tiers, qu'aucun contrôle ne juge. Un skill écrit ailleurs est un fichier
  Markdown comme un autre : le contrôle des références les parcourt déjà
  tous, donc une référence inventée y est refusée.

Restent à trancher : ce que le socle pose, la règle du « quand
nécessaire », et ce qu'un contrôle peut refuser dans un skill.

## Éléments cités

- B-0066@2e58f27d — le sujet du backlog ouvert sur la demande de Théo,
  avec les questions à régler avant d'écrire.
- B-0071@a3183a30 — le sujet du backlog sur le choix du modèle et de
  l'effort de chaque tâche, qui demande des sessions mesurées au banc.
- J-2026-10-19-C@e96c0a3a — la demande de Théo, texte exact, au journal.
- ADR-0031@ded211d6 — la décision qui fait échapper à tous les contrôles
  les fichiers d'un outil tiers déclarés une fois.

## Où regarder

- [les instructions de l'agent que pose l'installeur](https://github.com/theodubus/memory/blob/c198ed934d0e99a36c03a174a4f8210159a99431/engine/socle/templates/AGENTS.md) :
  les sections « Demandes de décision humaine », le paragraphe « Mémoire
  privée » et « Ce qui tourne tout seul », que l'option 1 sortirait en
  skills ; vérifier que le reste est fait de règles, pas de procédures.
- [l'installeur](https://github.com/theodubus/memory/blob/c198ed934d0e99a36c03a174a4f8210159a99431/engine/socle/installer.py),
  la table des outils tiers : les skills `bmad-*` y sont déclarés tiers.
- [le sujet du backlog](https://github.com/theodubus/memory/blob/c198ed934d0e99a36c03a174a4f8210159a99431/memory/backlog/B-0066-l-agent-ajoute-lui-meme-un-skill-quand-une-procedu.md) :
  les questions que la conception devait régler, et que les options
  ci-dessous tranchent.
- [BMad Builder sur npm](https://www.npmjs.com/package/bmad-builder/v/1.1.0) :
  ce que fait le module, s'il faut juger l'option 3.

## Options

1. **Le socle pose ses procédures rares en skills, l'agent écrit ceux du
   projet, deux contrôles les jugent.**
   - L'installeur pose `socle-demande` (poser une demande, relayer une
     réponse, consigner une décision en séance) et `socle-memoire-privee`
     dans le dossier des skills de Claude Code, protégés comme les hooks. `AGENTS.md` garde
     les règles et, pour chaque procédure sortie, une ligne qui donne le
     chemin de son fichier, lisible par tout agent. Les refus qui s'y
     rapportent (le lint d'une demande, par exemple) nomment le skill.
   - L'agent écrit un skill du projet la deuxième fois qu'il refait une
     même procédure, librement, avec une entrée au journal ; sans ADR. Il
     le nomme sans les préfixes `socle-` ni `bmad-`.
   - Deux contrôles, chacun avec son défaut injecté et un témoin sain :
     l'un vérifie le contrat d'un skill (son nom est celui de son dossier,
     sa description dit quand s'en servir, sa taille reste sous un seuil) ;
     l'autre juge chaque commande d'un skill comme le hook de l'agent la
     jugerait, et refuse le skill qui ferait lancer une commande refusée
     (action irréversible, contournement d'un hook, écriture d'un fichier
     protégé, commande réservée à l'humain).
   Effort : environ une journée. Risque faible à moyen : l'agent peut ne
   pas charger un skill quand il le faudrait, mais le refus qui nomme le
   skill le rattrape. Réversible : les skills sont des fichiers, et le
   texte revient dans `AGENTS.md`.
2. **Seulement les skills du projet et leurs deux contrôles**, sans
   toucher à `AGENTS.md`. Effort : une demi-journée. Risque faible.
   Réversible. Les instructions relues à chaque session ne s'allègent pas.
3. **S'appuyer sur BMad Builder** : `--with-bmad` installe aussi ce
   module, l'agent s'en sert sans interaction pour écrire ses skills, et le
   socle n'ajoute que le contrôle des commandes. Effort : une demi-journée,
   plus une dépendance de plus. Risque moyen : ses skills sortent là où
   l'agent ne les charge pas, et un projet sans BMAD n'a rien. Réversible.
4. **Refuser** : B-0066 est clos sans code.

## Conséquences

- Si Théo valide (option 1) : l'installeur, le gabarit des instructions,
  les deux contrôles et leurs défauts injectés s'écrivent, avec la
  documentation ; ce dépôt reçoit les skills du socle à la mise à jour.
- S'il choisit l'option 2 ou 3 : seule la partie correspondante s'écrit.
- S'il refuse : B-0066 est clos, rien ne change.
- Sans réponse : rien ne change ; je passe à B-0071.

## Recommandation

L'option 1.

Vérifié : la taille des sections de `AGENTS.md`, mesurée sur le gabarit ;
le contenu de BMAD Method 6.12.4 et de BMad Builder 1.1.0, lu dans leurs
paquets npm ; le contrôle des références parcourt tous les fichiers
Markdown, skills compris ; les skills de BMAD sont déclarés tiers.

Supposé : que Claude Code charge un skill de `.claude/skills/<nom>/` sur sa
description, comme sa documentation le dit, sans l'avoir mesuré ici ; que
d'autres agents (Codex) lisent le même format, non vérifié ; que le gain
au démarrage soit d'environ 3 Ko sur 11,4 Ko. La règle de la deuxième fois
ne se contrôle pas : aucun script ne reconnaît une procédure refaite ; le
journal la rend seulement visible.

## Réponses possibles

- `valider` — option 1 : les skills du socle, ceux du projet, et les deux contrôles.
- `projet-seul` — option 2 : les skills du projet et les deux contrôles, sans toucher aux instructions.
- `bmad-builder` — option 3 : BMad Builder installé avec BMAD, et le seul contrôle des commandes.
- `refuser` — B-0066 est clos sans code.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
