<!-- socle: couche=backlog zone=publique -->
# T-0184 — En mode amont, une copie d'un skill du socle identique à son gabarit passe protege.fichiers sans demande, et delegate-lot le dit

> statut : ouvert · origine : J-2026-11-25-V · besoin : B-0353 · lu : backlog@e34229f0

Un commit, dans L-0041, selon ADR-0110 (points 1, 2 et 5) : dans
`protege.fichiers` (`engine/socle/checks_ratchet.py`), en mode amont, la
copie `.claude/skills/socle-<nom>/SKILL.md` identique à son gabarit de la
même révision, dans la langue de la mémoire, passe sans demande, et une
copie retirée avec son gabarit aussi ; ses tests, dans un dépôt amont et
dans un projet ; `delegate-lot` dit la remise sans demande ;
l'architecture le dit.

## Fait quand

- [ ] en mode amont, une copie identique à son gabarit passe sans demande, une copie qui en diffère reste refusée, et un test le montre
- [ ] en mode projet, la copie identique à son gabarit reste refusée sans demande, et un test le montre
- [ ] `delegate-lot` dit la remise des copies sans demande
