<!-- socle: couche=backlog zone=publique -->
# T-0176 — Le gabarit de socle-batch, en français et en anglais, fait attendre les exécutions du commit poussé, par son SHA, et non la ligne « CI » de l'état ; une note de version ; la copie protégée remise

> statut : fait · origine : J-2026-11-24-AV · besoin : B-0350 · ref : J-2026-11-24-AX, D-0181 · lu : backlog@8bcdcc22

Un commit : l'étape 3 de `engine/socle/templates/skills/socle-batch/SKILL.md`
et de `SKILL.en.md` fait attendre la conclusion de toutes les exécutions
du commit poussé, par son SHA (`gh run list --commit <sha>`, en arrière-
plan), comme `delegate-lot` depuis ab70b8bc ; sans `gh` authentifié, un
réveil à l'heure probable de la fin, revérifié à chaque tour ; une note
de version ; le prompt de mise à jour de chess. La copie protégée de
`socle-batch` remise par l'installeur en mode amont, sur la demande
validée qui cite son empreinte.

## Fait quand

- [x] un test lit, dans le gabarit français et anglais de `socle-batch`, l'attente par le SHA du commit poussé, et non plus par la ligne « CI » de l'état
