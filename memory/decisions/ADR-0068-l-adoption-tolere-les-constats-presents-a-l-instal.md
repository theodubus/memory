<!-- socle: couche=decisions zone=publique -->
# ADR-0068 — L'adoption tolère les constats présents à l'installation, pas les nouveaux

> statut : acceptée · date : 2026-11-12 · lu : decisions@d48ef38a

## Contexte

Sous l'adoption, un contrôle nommé dans `[adoption] warn_only` voyait
toutes ses erreurs passer en avertissement, les nouvelles comme celles
d'avant l'installation (B-0180@fe4775a9, mesuré sur chess : une référence
inventée après l'installation passait). L'adoption promet des contrôles qui
ne peuvent que durcir. C'est un durcissement : décidé ici, sans demande.

## Décision

1. À l'adoption, l'installeur consigne, pour chaque contrôle de
   `warn_only`, les constats présents, dans la table
   `[adoption.tolerated]` des garde-fous (`.socle/guardrails.toml`, déjà
   soumis au cliquet) : `"<contrôle>" = ["<clé>", …]`. La clé d'un constat
   (`context.cle_de_constat`) est son fichier et son objet, séparés par
   « — » : l'objet est la valeur que le constat cite, posée par le contrôle
   (champ `objet` du constat), qui ne dépend ni de la langue ni de la
   tournure du message : `"LISEZMOI.md — absent.md"`,
   `"tests/test_a.py — sans assertion test_x"`.
   `memoire.references`, `tests.creux` et `docs.copie` le posent. Sans
   objet, la clé retombe sur le message dans sa langue source, le français
   (un message traduit garde sa source), sans numéro de ligne (celui qu'il
   porte dans son texte, `fichier.py:12` ou « ligne 12 », est effacé) ni
   blancs répétés. Deux constats de même clé s'écrivent deux fois et se
   comptent.
2. Au jugement, une erreur d'un contrôle de `warn_only` dont la clé reste
   à tolérer passe en avertissement, autant de fois que la liste la
   compte ; toute autre est une erreur. Un fichier que la plage renomme
   garde ses constats tolérés (la clé suit le renommage). Un constat
   toléré qui n'est plus observé se signale en avertissement, pour être
   retiré, à l'étage de la CI seulement : aux étages agent et git, un
   contrôle peut ne juger que les fichiers changés.
3. Le cliquet (sens `tolere`) : une liste qui apparaît durcit (absente, le
   contrôle entier était toléré) ; un constat de plus, au compte près,
   assouplit, et chaque constat ajouté se cite à part
   (`adoption.tolerated."<contrôle>" "<clé>"`) : une demande validée
   n'autorise que ceux qu'elle nomme ; une clé renommée avec son fichier
   n'assouplit pas ; la liste retirée alors que le contrôle reste dans
   `warn_only` assouplit ; retirer des constats, ou le contrôle avec sa
   liste, est libre.
4. Un projet adopté avant cette règle (`warn_only` sans liste) garde
   l'ancienne : le contrôle est désarmé en entier, il le dit à chaque
   passage, et l'état le dit avec son remède. À la mise à jour du moteur,
   l'installeur consigne les constats de la base (le point de divergence
   avec la branche par défaut distante) encore présents, et le dit ; un
   constat né sur la branche n'est pas toléré, l'installeur le nomme.
   Sans base lisible, il consigne les présents et le dit. Ses constats
   anciens restent des avertissements. Une liste déjà là n'est jamais
   étendue par l'installeur.
5. L'état et l'installeur disent, par contrôle, combien de constats
   l'adoption tolère encore ; à zéro, que le contrôle peut sortir de
   `warn_only`.

## Conséquences

Sous l'adoption, un constat nouveau fait échouer son contrôle, comme hors
adoption. Un contrôle sans objet garde une clé faite de son message en
français : une version du moteur qui le reformule rend ses constats
anciens erreurs, à corriger ou à tolérer de nouveau par une demande
validée ; un contrôle que l'adoption met souvent en `warn_only` reçoit
donc son objet.
Un défaut injecté (une référence morte née après l'adoption, refusée au
commit) et un témoin (une d'avant, déplacée d'une ligne, qui reste en
avertissement) l'éprouvent. Pour défaire : retirer la table et ce
jugement, l'adoption retombe sur le contrôle désarmé en entier.
