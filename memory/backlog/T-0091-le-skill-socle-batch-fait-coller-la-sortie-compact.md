<!-- socle: couche=backlog zone=publique -->
# T-0091 — Le skill socle-batch fait coller la sortie compacte de socle roadmap dans un bloc de code : collée en texte, sa ligne « Ensuite : » tient lieu de celle du récap (ADR-0089)

> statut : ouvert · origine : J-2026-11-18-R · besoin : B-0274 · lu : backlog@4fa0e025

Relevé à la correction des bloquants de la passe 1 de L-0016
(J-2026-11-18-R). Le hook de fin de tour ne lit plus les deux lignes du
récap dans un bloc de code (ADR-0089) : un compact de `socle roadmap`
collé dans un bloc ne tient plus lieu de la ligne « Ensuite : » du récap.
Collé en texte, il le fait encore. Le skill `socle-batch` (gabarit
`engine/socle/templates/skills/socle-batch/SKILL.md`, point 5 de
« Intégrer, pousser, livrer », et son anglais) dit de coller la sortie
au récap de la clôture d'un lot sans dire où ; le skill `delegate-lot`
de l'atelier de même, à l'annonce et à la clôture. Le livrable, un
commit : les deux skills disent de la coller dans un bloc de code ; la
copie protégée de `socle-batch` suit la règle de L-0006 sur la remise
des copies.

## Fait quand

- [ ] le gabarit du skill socle-batch, son anglais et le skill delegate-lot disent de coller la sortie compacte de socle roadmap dans un bloc de code, et un test de `tests/test_suite_du_projet.py` lit la phrase
