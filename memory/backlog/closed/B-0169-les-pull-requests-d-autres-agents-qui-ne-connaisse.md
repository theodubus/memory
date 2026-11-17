<!-- socle: couche=backlog zone=publique -->
# B-0169 — Les pull requests d'autres agents, qui ne connaissent pas le socle, sont jugées par le travail de CI du socle, même sous des chemins déclarés tiers

> statut : fait · origine : ADR-0059 · lu : backlog@f646bf36 · ref : J-2026-11-11-T

L'essai à blanc sur chess (`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`, partie 2) : d'autres sessions
travaillent sous un sous-dossier de chess sans connaître le socle, et
leurs commits, co-signés par un agent, ne portent pas la trace des hooks.
Le travail de CI du socle jugerait leurs pull requests. Déclarer ce
sous-dossier tiers est peut-être la réponse ; rien ne l'a éprouvé.

## Satisfait quand

- [x] une pull request dont les commits, co-signés par un agent sans les hooks du socle, ne touchent que des chemins déclarés tiers passe le travail de CI du socle, et un test le montre ; ou ce qui la fait échouer est dit, avec le réglage qui la laisse passer
