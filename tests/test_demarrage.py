"""B-0010, ADR-0071 : la sortie du démarrage tient sous la borne des
garde-fous (`[startup] max_bytes`), que Claude Code remet entière à
l'agent, chaque partie dans sa part : l'état dérivé d'abord, ses lignes
bornées et ses listes plafonnées, son essentiel dans les 2 000 premiers
octets ; puis le chantier actif, les faits par leur titre et les dix
dernières décisions. Une partie au-delà de ce qui lui revient perd des
lignes entières depuis sa fin sans toucher à la part d'une autre, et une
dernière ligne dit ce qui est coupé, de combien, et où le lire."""

import contextlib
import io
import os
import re
import shlex
import shutil
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path
from unittest import mock

from socle import config, hooks, installer as installeur, state as etat, utils as outils, verification
from socle.checks_ratchet import assouplissements
from tests.test_bascule import MOTEUR, git

ACTIF = """<!-- socle: couche=actif zone=publique -->
# Chantier actif

## En cours

{lignes}
"""


def decision(n: int, statut: str = "acceptée") -> str:
    return (f"<!-- socle: couche=decisions zone=publique -->\n"
            f"# ADR-{n:04d} — La décision numéro {n}, au titre assez long pour peser dans un index entier\n\n"
            f"> statut : {statut} · date : 2026-10-{10 + n % 18:02d}\n\n## Décision\n\nLa décision {n}.\n")


def fait(n: int, statut: str = "mesuré · preuve : fichier:calc.py") -> str:
    return f"## F-{n:04d} — Le fait numéro {n}, mesuré sur le projet d'essai\n\n> statut : {statut}\n\nSon détail.\n\n"


def sujet(n: int, statut: str = "ouvert", priorite: str = "") -> str:
    meta = f"> statut : {statut} · origine : fichier:calc.py" + (f" · priorité : {priorite}" if priorite else "")
    return (f"<!-- socle: couche=backlog zone=publique -->\n# B-{n:04d} — Le sujet numéro {n}, au titre assez long "
            f"pour qu'une ligne de l'état dérivé le raccourcisse\n\n{meta}\n\nPour l'essai.\n")


def demande(n: int) -> str:
    return (f"<!-- socle: couche=demandes zone=publique -->\n# D-{n:04d} — La demande numéro {n}, en attente de "
            f"l'humain\n\n> date : 2026-11-12\n\n## Question posée\n\nTrancher.\n")


def chantier_actif(zone: str, taille: int) -> str:
    """Un chantier actif de `taille` octets exactement, en lignes entières."""
    texte = f"<!-- socle: couche=actif zone={zone} -->\n# Chantier actif\n\n## En cours\n\n"
    k = 1
    while len(texte.encode("utf-8")) + 60 < taille:
        texte += f"- Étape {k} du chantier, dite sur une ligne entière.\n"
        k += 1
    return texte + "x" * (taille - len(texte.encode("utf-8")) - 1) + "\n"


def octets(texte: str) -> int:
    """La taille imprimée, saut de ligne final compris."""
    return len((texte + "\n").encode("utf-8"))


def entre(lignes: list[str], debut: str, fin: str) -> list[str]:
    """Les lignes d'un groupe de la sortie : de l'en-tête qui commence par
    `debut`, avec la ligne vide qui le précède, jusqu'à la ligne qui
    commence par `fin`, sans la ligne vide qui la précède."""
    i = next(k for k, l in enumerate(lignes) if l.startswith(debut)) - 1
    j = next(k for k, l in enumerate(lignes) if k > i and l.startswith(fin))
    return lignes[i:j - 1 if lignes[j - 1] == "" else j]


class Demarrage(unittest.TestCase):
    """Un projet installé, public, sur une branche de travail : quarante
    décisions, vingt faits, un chantier actif de quarante lignes, une
    demande en attente, sept commits non fusionnés, un backlog de huit
    sujets prêts, douze de priorité basse et un en cours."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-demarrage-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        decisions = self.racine / "memory/decisions"
        decisions.mkdir(exist_ok=True)
        for n in range(1, 41):
            (decisions / f"ADR-{n:04d}-decision-{n}.md").write_text(decision(n, "remplacée" if n == 35 else "acceptée"))
        self.faits(20)
        self.actif(40)
        backlog = self.racine / "memory/backlog"
        backlog.mkdir(exist_ok=True)
        for n in range(1, 22):
            (backlog / f"B-{n:04d}-sujet-{n}.md").write_text(sujet(
                n, "en cours" if n == 21 else "ouvert", "haute" if n == 3 else "basse" if n > 8 else ""))
        self.demande(1)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        git(self.racine, "checkout", "-qb", "travail")
        for n in range(1, 8):
            git(self.racine, "commit", "-qm", f"Le travail numéro {n}, au sujet assez long pour que l'état dérivé le "
                                              "raccourcisse", "--allow-empty", "--no-verify")

    def faits(self, n: int):
        canonique = self.racine / "memory/canonical.md"
        entete = canonique.read_text().split("\n## ", 1)[0].rstrip() + "\n\n"
        canonique.write_text(entete + "".join(fait(k, "supposé · source : calc.py" if k == 7 else
                                                   "mesuré · preuve : fichier:calc.py") for k in range(1, n + 1)))

    def actif(self, n: int):
        (self.racine / "memory/active.md").write_text(ACTIF.format(lignes="\n".join(
            f"- Étape {k} du chantier en cours, dite sur une ligne entière." for k in range(1, n + 1))))

    def demande(self, n: int):
        requetes = self.racine / "memory/requests"
        requetes.mkdir(exist_ok=True)
        (requetes / f"D-{n:04d}-demande-{n}.md").write_text(demande(n))

    def projet(self, borne: int | None = None) -> config.Projet:
        if borne is not None:
            gf = self.racine / ".socle/guardrails.toml"
            texte, n = re.subn(r"(\[startup\][^\[]*?)max_bytes = \d+", rf"\g<1>max_bytes = {borne}", gf.read_text())
            self.assertEqual(n, 1)
            gf.write_text(texte)
        return config.Projet.charger(self.racine)

    def sortie(self, borne: int | None = None) -> str:
        return etat.calculer(self.projet(borne))

    def etat_derive(self, sortie: str) -> str:
        return sortie.split("\n\n--- memory/active.md ---", 1)[0]

    def test_l_essentiel_tient_dans_les_2000_premiers_octets_d_un_etat_qui_les_depasse(self):
        """Le 3e critère de B-0010, sur un état dérivé qui ne tient pas
        entier dans l'aperçu de Claude Code : ce qui demande d'agir y est en
        tête, puis ce qui informe, dans cet ordre, et le backlog vient après."""
        sortie = self.sortie()
        self.assertGreater(octets(self.etat_derive(sortie)), 2000)
        premiers = sortie.encode("utf-8")[:2000].decode("utf-8", errors="ignore")
        ordre = ["== ", "ce qui revient à l'humain : 1", "  décision : D-0001 — La demande numéro 1",
                 "demandes humaines en attente : 1", "commit   :", "base     :", "CI       :", "branche  :",
                 "mémoire  :", "hooks    :", "mémoire privée :", "backlog  :"]
        positions = []
        for debut in ordre:
            ligne = next((l for l in premiers.splitlines() if l.startswith(debut)), None)
            self.assertIsNotNone(ligne, f"« {debut} » hors des 2 000 premiers octets")
            positions.append(premiers.index(ligne))
        self.assertEqual(positions, sorted(positions))
        self.assertLess(sortie.index("backlog  :"), sortie.index("vérifier :"))
        self.assertNotIn("ADR-", premiers)
        self.assertLess(sortie.index("--- memory/active.md ---"), sortie.index("--- memory/canonical.md"))
        self.assertLess(sortie.index("--- memory/canonical.md"), sortie.index("dernières décisions sur 40"))

    def test_une_demande_en_attente_ne_compte_pas_deux_fois(self):
        sortie = self.sortie()
        self.assertEqual(sortie.count("D-0001"), 1)
        self.assertIn("demandes humaines en attente : 1 — sous « ce qui revient à l'humain », avec leur lien", sortie)
        self.assertIn("  décision : D-0001 — La demande numéro 1, en attente de l'humain", sortie)

    def test_les_listes_de_l_etat_derive_sont_plafonnees_et_ses_lignes_bornees(self):
        for n in range(2, 8):
            self.demande(n)
        lignes = self.etat_derive(self.sortie()).splitlines()
        # Les commits non fusionnés.
        i = next(k for k, l in enumerate(lignes) if l.startswith("base     :"))
        self.assertEqual(lignes[i], "base     : main — non fusionné : 7 commit(s)")
        self.assertEqual(len([l for l in lignes[i + 1:] if re.match(r"  [0-9a-f]{7} Le travail", l)]),
                         etat.COMMITS_MONTRES)
        self.assertEqual(lignes[i + 1 + etat.COMMITS_MONTRES],
                         "  … et 2 autre(s) : `python3 .socle/socle state --short`")
        # Ce qui revient à l'humain : les demandes en attente, chacune avec son
        # lien ; au-delà, leur nombre et où les lire.
        i = lignes.index("ce qui revient à l'humain : 7")
        self.assertEqual([l.split(" — ")[0] for l in lignes[i + 1:i + 1 + 2 * etat.ELEMENTS_MONTRES:2]],
                         [f"  décision : D-{n:04d}" for n in range(1, 5)])
        self.assertEqual(lignes[i + 1 + 2 * etat.ELEMENTS_MONTRES],
                         "  … et 3 autre(s) : `python3 .socle/socle state --short`")
        # Les sujets en cours et prêts, leurs titres raccourcis ; les basses.
        titre = sujet(21).splitlines()[1].split(" — ", 1)[1]
        self.assertIn(f"  en cours : B-0021 — {outils.raccourcir(titre, etat.TITRE_DE_SUJET)}", lignes)
        self.assertTrue(outils.raccourcir(titre, etat.TITRE_DE_SUJET).endswith("…"))
        prets = [l for l in lignes if l.startswith("  prêt : ")]
        self.assertEqual(len(prets), etat.PRETS_MONTRES)
        titre = sujet(3).splitlines()[1].split(" — ", 1)[1]
        self.assertEqual(prets[0], f"  prêt : B-0003 — {outils.raccourcir(titre, etat.TITRE_DE_SUJET)} (priorité haute)")
        self.assertIn("  … et 3 autre(s) prêt(s)", lignes)
        self.assertIn("  prêts aussi, de priorité basse : " + ", ".join(f"B-{n:04d}" for n in range(9, 19))
                      + " … et 2 autre(s)", lignes)
        self.assertLessEqual(max(len(l.encode("utf-8")) for l in lignes), etat.LIGNE)
        # `socle state --short` : l'état dérivé entier, sans plafond.
        court = etat.calculer(self.projet(), contenus=False)
        self.assertEqual(len(re.findall(r"(?m)^  [0-9a-f]{7} Le travail", court)), 7)
        self.assertEqual(len(re.findall(r"(?m)^  décision : D-", court)), 7)
        self.assertEqual(len(re.findall(r"(?m)^  prêt : ", court)), 8)
        self.assertNotIn("… et", court)

    def test_sous_la_borne_rien_ne_se_coupe(self):
        sortie = self.sortie()
        self.assertLessEqual(octets(sortie), 9500)
        self.assertNotIn("!! coupé", sortie)
        lignes = sortie.splitlines()
        # Le chantier actif entier.
        self.assertIn("- Étape 40 du chantier en cours, dite sur une ligne entière.", lignes)
        # Les faits par leur titre, le statut quand il n'est pas « mesuré ».
        self.assertIn("--- memory/canonical.md : 20 fait(s) par leur titre ; un en entier : `python3 .socle/socle "
                      "show F-NNNN` ---", lignes)
        self.assertIn("F-0001 — Le fait numéro 1, mesuré sur le projet d'essai", lignes)
        self.assertIn("F-0007 — Le fait numéro 7, mesuré sur le projet d'essai (supposé)", lignes)
        self.assertNotIn("Son détail.", sortie)
        # Les dix dernières décisions, la plus récente d'abord, et leur nombre ;
        # le statut dans la langue du projet, le titre raccourci.
        debut = lignes.index("--- les 10 dernières décisions sur 40, la plus récente d'abord ; avant toute décision "
                             "de conception, l'index entier : `python3 .socle/socle show --index decisions` ---")
        self.assertEqual([l.split(" — ")[0] for l in lignes[debut + 1:]],
                         [f"ADR-{n:04d}" for n in (35, 17, 34, 16, 33, 15, 32, 14, 31, 13)])
        self.assertRegex(lignes[debut + 1], r"^ADR-0035 — La décision numéro 35, au titre assez long.*… \(remplacée\)$")
        self.assertLessEqual(max(len(l.encode("utf-8")) for l in lignes[debut + 1:]), etat.TITRE)
        self.assertNotIn("decisions@", sortie)

    def test_le_statut_d_une_decision_dans_la_langue_du_projet(self):
        with mock.patch("socle.language.du_projet", return_value="en"):
            parties = etat.parties_injectees(self.projet(), etat.memoire.Memoire.charger(self.racine))
        self.assertTrue(parties[-1].lignes[0].endswith(" (superseded)"), parties[-1].lignes[0])
        self.assertTrue(any(l.endswith(" (assumed)") for l in parties[1].lignes))

    def test_l_en_tete_des_decisions_dit_le_nombre_montre(self):
        decisions = etat.parties_injectees(self.projet(), etat.memoire.Memoire.charger(self.racine))[-1]
        self.assertEqual(decisions.groupe, "decisions")
        self.assertEqual(decisions.entete(1, 10)[1], "--- la dernière décision sur 40 ; avant toute décision de "
                                                     "conception, l'index entier : `python3 .socle/socle show --index "
                                                     "decisions` ---")
        self.assertTrue(decisions.entete(3, 10)[1].startswith("--- les 3 dernières décisions sur 40, "))

    def test_le_chantier_actif_au_dela_de_sa_part_se_coupe_seul_et_dit_son_chemin(self):
        """Le chantier actif en dernier recours : ce que les autres laissent
        de leur part lui revient, il perd sa fin, et rien d'autre."""
        self.actif(120)
        sortie = self.sortie()
        lignes = sortie.splitlines()
        self.assertLessEqual(octets(sortie), 9500)
        actif = [l for l in lignes if l.startswith("- Étape ")]
        self.assertEqual(actif, [f"- Étape {k} du chantier en cours, dite sur une ligne entière."
                                 for k in range(1, len(actif) + 1)])
        self.assertLess(len(actif), 120)
        self.assertGreater(len(actif), 50)  # sa part, et ce que les autres en laissent
        self.assertIn("vérifier :", sortie)
        self.assertEqual(len([l for l in lignes if l.startswith("F-")]), 20)
        self.assertEqual(len([l for l in lignes if l.startswith("ADR-")]), 10)
        self.assertRegex(lignes[-1], r"^!! coupé à la borne du démarrage \(9500 octets, `\[startup\] max_bytes` des "
                                     r"garde-fous\) : le chantier actif, \d+ octets pour une part de 3800 — la fin du "
                                     r"chantier actif, \d+ ligne\(s\) sur 125 : lire memory/active\.md$")

    def test_les_faits_au_dela_de_leur_part_se_coupent_sans_toucher_aux_decisions(self):
        self.faits(80)
        self.actif(55)
        sortie = self.sortie()
        lignes = sortie.splitlines()
        self.assertLessEqual(octets(sortie), 9500)
        self.assertIn("- Étape 55 du chantier en cours, dite sur une ligne entière.", lignes)
        self.assertEqual(len([l for l in lignes if l.startswith("ADR-")]), 10)
        faits = [l for l in lignes if l.startswith("F-")]
        self.assertTrue(0 < len(faits) < 80)
        self.assertEqual(faits[-1].split(" — ")[0], f"F-{len(faits):04d}")
        self.assertIn(f"--- memory/canonical.md : {len(faits)} fait(s) sur 80 par leur titre ; un en entier : "
                      "`python3 .socle/socle show F-NNNN` ---", lignes)
        self.assertRegex(lignes[-1], r" : les faits, \d+ octets pour une part de 2090 — "
                                     rf"{80 - len(faits)} fait\(s\) sur 80 : lire memory/canonical\.md$")

    def test_quand_tout_depasse_chaque_partie_garde_sa_part(self):
        """Aucune partie ne mange celle d'une autre : sans rien à partager,
        chacune tient dans sa part, et la ligne de coupe les dit toutes."""
        self.actif(120)
        self.faits(80)
        for n in range(2, 8):
            self.demande(n)
        borne = 5000
        sortie = self.sortie(borne)
        lignes = sortie.splitlines()
        self.assertLessEqual(octets(sortie), borne)
        groupes = {"etat": lignes[:lignes.index("--- memory/active.md ---") - 1],
                   "actif": entre(lignes, "--- memory/active.md ---", "--- memory/canonical.md"),
                   "faits": entre(lignes, "--- memory/canonical.md", "--- les "),
                   "decisions": entre(lignes, "--- les ", "!! coupé")}
        for groupe, contenu in groupes.items():
            self.assertLessEqual(sum(len(l.encode("utf-8")) + 1 for l in contenu), int(borne * etat.PARTS[groupe]),
                                 groupe)
        montrees = len([l for l in lignes if l.startswith("ADR-")])
        self.assertIn(f"--- les {montrees} dernières décisions sur 40, ", sortie)
        note = lignes[-1]
        for debut in ("l'état dérivé, ", "le chantier actif, ", "les faits, ", "les décisions, "):
            self.assertIn(debut, note)
        self.assertIn("`python3 .socle/socle state --short`", note)
        self.assertIn(f"{10 - montrees} des 10 dernières décisions : `python3 .socle/socle show --index decisions`",
                      note)

    def test_la_sortie_du_hook_reste_sous_la_borne_avec_une_ligne_d_outil_de_plusieurs_ko(self):
        """Un échec des outils en session cloud dont la sortie finit par une
        ligne de pip de plusieurs Ko : la ligne est bornée, et la sortie du
        hook, lignes du hook comprises, tient sous la borne."""
        commande = f"{shlex.quote(sys.executable)} -c 'print(\"from versions: \" + \"1.0, \" * 1200); raise SystemExit(1)'"
        projet = self.projet()
        with mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: "true"}), \
                mock.patch.object(verification, "commandes_ci", return_value=[commande]), \
                mock.patch.object(verification, "commandes_en_attente", return_value=[]), \
                mock.patch.object(hooks, "installer_hooks_git", return_value=False), \
                contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(hooks.session_start(projet, {}), 0)
        sortie = flux.getvalue()
        self.assertLessEqual(len(sortie.encode("utf-8")), 9500)
        lignes = sortie.splitlines()
        echec = next(k for k, l in enumerate(lignes) if l.startswith("!! outils de l'adaptateur : "))
        self.assertTrue(lignes[echec + 1].startswith("    from versions: 1.0, "))
        self.assertLessEqual(len(lignes[echec + 1].encode("utf-8")), 4 + hooks.LIGNE_DE_SORTIE)
        self.assertLess(echec, lignes.index("!! hooks git non branchés : `git config core.hooksPath .socle/git-hooks`"))
        self.assertLess(echec, next(k for k, l in enumerate(lignes) if l.startswith("backlog  :")))
        self.assertIn("- Étape 40 du chantier en cours, dite sur une ligne entière.", lignes)

    def test_la_coupe_de_l_etat_atteint_les_lignes_du_hook_en_dernier_et_dit_ou_les_lire(self):
        """Quarante échecs des outils, chacun de plusieurs Ko : la coupe de
        l'état retire d'abord ce qui se relit ailleurs (les commits, le
        backlog), puis ce qui informe, puis les blocs du hook depuis la fin,
        chacun entier ; ce qui revient à l'humain reste. La ligne de coupe
        renvoie à `socle state --short`, qui redit toutes les lignes du
        hook."""
        projet = self.projet()
        crue = [f"!! outils de l'adaptateur : `commande {n}` a rendu 1\n    " + "x" * 3000 for n in range(40)]
        with mock.patch.object(hooks, "installer_outils", return_value=list(crue)), \
                mock.patch.object(hooks, "installer_hooks_git", return_value=True), \
                contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(hooks.session_start(projet, {}), 0)
        sortie = flux.getvalue()
        lignes = sortie.splitlines()
        self.assertLessEqual(len(sortie.encode("utf-8")), 9500)
        self.assertLessEqual(max(len(l.encode("utf-8")) for l in lignes), etat.LIGNE)
        for ligne in ("ce qui revient à l'humain : 1", "  décision : D-0001 — La demande numéro 1, en attente de l'humain",
                      "demandes humaines en attente : 1 — sous « ce qui revient à l'humain », avec leur lien"):
            self.assertIn(ligne, lignes)
        montres = [k for k, l in enumerate(lignes) if l.startswith("!! outils de l'adaptateur : ")]
        self.assertTrue(0 < len(montres) < 40, len(montres))
        self.assertEqual([lignes[k] for k in montres],
                         [f"!! outils de l'adaptateur : `commande {n}` a rendu 1" for n in range(len(montres))])
        self.assertTrue(all(lignes[k + 1].startswith("    xxx") for k in montres))
        for debut in ("commit   :", "base     :", "CI       :", "mémoire  :", "backlog  :", "  prêt :", "vérifier :"):
            self.assertFalse(any(l.startswith(debut) for l in lignes), debut)
        # Le chantier actif garde sa part.
        self.assertIn("- Étape 40 du chantier en cours, dite sur une ligne entière.", lignes)
        self.assertRegex(lignes[-1], r" : l'état dérivé, \d+ octets pour une part de 2375 — \d+ ligne\(s\) sur \d+ ; "
                                     r"l'état entier : `python3 \.socle/socle state --short`$")
        # Ce que la ligne de coupe désigne contient ce qui est coupé.
        court = etat.calculer(projet, contenus=False)
        self.assertRegex(court, r"(?m)^au dernier démarrage de session \(\d{4}-\d\d-\d\dT[^)]*\), le hook a ajouté :$")
        self.assertEqual(len(re.findall(r"(?m)^  !! outils de l'adaptateur : `commande \d+` a rendu 1$", court)), 40)
        for debut in ("commit   :", "backlog  :", "vérifier :"):
            self.assertIn(debut, court)
        # Gardées à côté de la trace des hooks, hors de l'arbre ; un démarrage
        # sans lignes du hook n'en laisse rien.
        self.assertEqual(etat.chemin_demarrage(self.racine), config.chemin_trace(self.racine).parent / "startup.json")
        self.assertTrue(etat.chemin_demarrage(self.racine).is_file())
        self.assertIn(".git", etat.chemin_demarrage(self.racine).relative_to(self.racine).parts)
        with mock.patch.object(hooks, "installer_outils", return_value=[]), \
                mock.patch.object(hooks, "installer_hooks_git", return_value=True), \
                contextlib.redirect_stdout(io.StringIO()):
            hooks.session_start(projet, {})
        self.assertFalse(etat.chemin_demarrage(self.racine).exists())
        self.assertNotIn("le hook a ajouté", etat.calculer(projet, contenus=False))

    def test_une_borne_baissee_garde_les_demandes_et_ce_qui_revient_a_l_humain(self):
        """À 4 000 octets, la part de l'état ne tient plus ses listes : ce qui
        se relit ailleurs part, ce qui demande d'agir reste. La borne, passée
        sous ce qu'il faut au chantier actif, est signalée."""
        for n in range(2, 7):
            self.demande(n)
        self.faits(40)
        (self.racine / "memory/active.md").write_text(chantier_actif("publique", 3700))
        sortie = self.sortie(4000)
        lignes = sortie.splitlines()
        self.assertLessEqual(octets(sortie), 4000)
        self.assertIn("ce qui revient à l'humain : 6", lignes)
        for n in range(1, 5):
            self.assertIn(f"  décision : D-{n:04d} — La demande numéro {n}, en attente de l'humain", lignes)
        self.assertIn("  … et 2 autre(s) : `python3 .socle/socle state --short`", lignes)
        self.assertIn("demandes humaines en attente : 6 — sous « ce qui revient à l'humain », avec leur lien", lignes)
        self.assertFalse(any(re.match(r"  [0-9a-f]{7} Le travail", l) for l in lignes))
        self.assertFalse(any(l.startswith(("backlog  :", "  prêt :")) for l in lignes))
        self.assertIn(" : l'état dérivé, ", lignes[-1])
        court = etat.calculer(self.projet(), contenus=False)
        alerte = ("!! le budget de memory/active.md (3700 octets, public et privé ensemble) dépasse la part du "
                  "chantier actif dans la sortie du démarrage (1540 octets, en-têtes déduits) : à son budget, il y "
                  "serait coupé à chaque session ; le baisser à 1540 au plus")
        self.assertTrue(etat.alerte_budget_actif(self.projet())[0].startswith(alerte))
        self.assertIn(alerte, court)
        self.assertEqual(etat.alerte_budget_actif(self.projet(9500)), [])
        self.assertNotIn("!! le budget de", etat.calculer(self.projet(), contenus=False))

    def test_les_demandes_en_attente_se_disent_quoi_qu_il_arrive_a_ce_qui_revient_a_l_humain(self):
        """Une régression de la première correction : seule la liste de ce
        qui revient à l'humain nommait les demandes, et un échec de son calcul,
        ou de celui du balayage de mutation, les taisait toutes."""
        from socle import human as humain, mutation

        self.demande(2)
        (self.racine / "memory/requests/D-0003-sans-titre.md").write_text("Une demande sans son en-tête.\n")
        with mock.patch.object(mutation, "etat_du_balayage", side_effect=RuntimeError("gh hors service")):
            lignes = self.sortie().splitlines()
        self.assertIn("ce qui revient à l'humain : 2", lignes)
        self.assertIn("  décision : D-0001 — La demande numéro 1, en attente de l'humain", lignes)
        self.assertIn("mutation : état inconnu (RuntimeError: gh hors service)", lignes)
        with mock.patch.object(humain, "a_faire", side_effect=RuntimeError("panne")):
            lignes = self.sortie().splitlines()
            court = etat.calculer(self.projet(), contenus=False)
        self.assertIn("ce qui revient à l'humain : incalculable (RuntimeError: panne)", lignes)
        i = lignes.index("demandes humaines en attente : 3")
        self.assertEqual(lignes[i + 1:i + 6], [
            "  décision : D-0001 — La demande numéro 1, en attente de l'humain", "    (pas encore poussée : pas de lien)",
            "  décision : D-0002 — La demande numéro 2, en attente de l'humain", "    (pas encore poussée : pas de lien)",
            "  illisible : memory/requests/D-0003-sans-titre.md — `python3 .socle/socle check` dit pourquoi"])
        # Au-delà du plafond, la ligne dit où lire les autres, que l'état entier donne.
        for n in range(4, 8):
            self.demande(n)
        with mock.patch.object(humain, "a_faire", side_effect=RuntimeError("panne")):
            lignes = self.sortie().splitlines()
            court = etat.calculer(self.projet(), contenus=False)
        i = lignes.index("demandes humaines en attente : 7")
        self.assertEqual(lignes[i + 2 * etat.ELEMENTS_MONTRES],
                         "  … et 3 autre(s) : `python3 .socle/socle state --short`")
        self.assertEqual(len(re.findall(r"(?m)^  décision : D-\d{4} — ", court)), 6)
        self.assertIn("  illisible : memory/requests/D-0003-sans-titre.md", court)

    def test_la_borne_vient_des_garde_fous_celle_du_gabarit_a_defaut(self):
        self.assertEqual(self.projet().borne_demarrage(), 9500)
        self.assertEqual(self.projet(7000).borne_demarrage(), 7000)
        projet = self.projet()
        for valeur in (None, 0, -5, "beaucoup", True):
            projet.garde_fous["startup"] = {} if valeur is None else {"max_bytes": valeur}
            self.assertEqual(projet.borne_demarrage(), config.BORNE_DEMARRAGE)

    def test_le_chantier_actif_dans_son_budget_n_est_jamais_coupe_quoi_que_pesent_les_autres(self):
        """Public et privé, deux parties d'un même groupe : le budget du
        chantier actif juge leur somme, et leur part la tient, leurs deux
        en-têtes déduits. À leur budget, ils ne sont jamais coupés, même
        quand l'état et les faits débordent de la leur et prennent ce que les
        décisions laissent."""
        from socle import context as contexte

        projet = self.projet()
        permis = etat.budget_actif_permis(projet)
        self.assertEqual(permis, 3800 - len("\n--- memory/active.md ---\n") - len("\n--- memory/private/active.md ---\n"))
        for nom in ("guardrails.toml", "guardrails.en.toml"):
            gf = tomllib.loads((MOTEUR / "socle/templates" / nom).read_text(encoding="utf-8"))
            self.assertLessEqual(gf["budgets"]["memory/active.md"]["max_bytes"], permis, nom)
        politique = self.racine / ".socle/policy.toml"
        politique.write_text(politique.read_text() + '\n[private]\nmode = "chiffre"\n')
        (self.racine / "memory/private").mkdir()
        self.faits(80)
        for n in range(2, 8):
            self.demande(n)
        etat.retenir_demarrage(projet, [f"!! outils de l'adaptateur : `commande {n}` a rendu 1\n    " + "x" * 900
                                        for n in range(4)])
        budget = projet.budget_octets("memory/active.md")
        self.assertEqual(budget, 3700)
        for public, prive in ((budget, 0), (budget // 3, budget - budget // 3), (budget, budget)):
            with self.subTest(public=public, prive=prive):
                (self.racine / "memory/active.md").write_text(chantier_actif("publique", public))
                (self.racine / "memory/private/active.md").unlink(missing_ok=True)
                if prive:
                    (self.racine / "memory/private/active.md").write_text(chantier_actif("privee", prive))
                projet = self.projet()
                rapport = contexte.executer(contexte.Contexte(projet, etage="git"), ["memoire.budgets"])
                if public + prive > budget:
                    self.assertFalse(rapport.reussi)
                    self.assertIn(f"{public} + {prive} octets pour le chantier actif public et privé, qui partagent "
                                  f"une part de la sortie du démarrage, pour un budget de {budget} à eux deux",
                                  rapport.texte())
                    continue
                self.assertTrue(rapport.reussi, rapport.texte())
                lignes = self.sortie().splitlines()
                self.assertLessEqual(octets("\n".join(lignes)), 9500)
                self.assertIn(" : l'état dérivé, ", lignes[-1])
                self.assertIn(" ; les faits, ", lignes[-1])
                self.assertNotIn("le chantier actif", lignes[-1])
                self.assertEqual(entre(lignes, "--- memory/active.md ---", "--- memory/private/active.md" if prive
                                       else "--- memory/canonical.md")[2:],
                                 chantier_actif("publique", public).rstrip().splitlines())
                if prive:
                    self.assertEqual(entre(lignes, "--- memory/private/active.md ---", "--- memory/canonical.md")[2:],
                                     chantier_actif("privee", prive).rstrip().splitlines())

    def test_une_mise_a_jour_signale_un_budget_du_chantier_actif_au_dela_de_sa_part(self):
        """Un projet installé avant gardait 6 000 octets pour son chantier
        actif : la mise à jour garde ses garde-fous, et le dit."""
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace('"memory/active.md" = { max_bytes = 3700 }',
                                             '"memory/active.md" = { max_bytes = 6000 }'))
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertIn("!! le budget de memory/active.md (6000 octets, public et privé ensemble) dépasse la part du "
                      "chantier actif dans la sortie du démarrage (3740 octets, en-têtes déduits) : à son budget, il y "
                      "serait coupé à chaque session ; le baisser à 3740 au plus", flux.getvalue())
        self.assertIn("max_bytes = 6000", gf.read_text())
        gf.write_text(gf.read_text().replace("max_bytes = 6000", "max_bytes = 3740"))
        self.assertEqual(installeur.alerte_chantier_actif(self.racine), [])
class TestBorner(unittest.TestCase):
    """Le partage de la borne, sur des parties de lignes de 100 octets."""

    def setUp(self):
        patch = mock.patch.dict(etat.PARTS, {"etat": 0.4, "a": 0.3, "b": 0.3}, clear=True)
        patch.start()
        self.addCleanup(patch.stop)

    @staticmethod
    def partie(groupe: str, n: int) -> etat.Partie:
        return etat.Partie(groupe, [f"{groupe}{i}".ljust(99, ".") for i in range(1, n + 1)],
                           lambda k, t, g=groupe: f"{k}/{t} de {g}",
                           (lambda m, t, g=groupe: ["", f"--- {g} ---"]) if groupe != "etat" else etat._sans_entete)

    def test_tout_tient_rien_ne_se_coupe(self):
        parties = [self.partie("etat", 2), self.partie("a", 3), self.partie("b", 3)]
        self.assertEqual(etat.borner(parties, 1000),
                         [*parties[0].lignes, "", "--- a ---", *parties[1].lignes, "", "--- b ---", *parties[2].lignes])

    def test_un_groupe_au_dela_de_sa_part_prend_ce_que_les_autres_laissent_et_perd_sa_fin(self):
        parties = [self.partie("etat", 2), self.partie("a", 3), self.partie("b", 6)]
        res = etat.borner(parties, 1000)
        self.assertLessEqual(sum(len(l.encode()) + 1 for l in res), 1000)
        # a reste entier ; b garde sa part (300) et ce que l'état laisse de la sienne.
        self.assertEqual(res[:-1], [*parties[0].lignes, "", "--- a ---", *parties[1].lignes, "", "--- b ---",
                                    *parties[2].lignes[:3]])
        self.assertEqual(res[-1], "!! coupé à la borne du démarrage (1000 octets, `[startup] max_bytes` des "
                                  "garde-fous) : b, 611 octets pour une part de 300 — 3/6 de b")

    def test_une_partie_ne_mange_pas_la_part_d_une_autre(self):
        parties = [self.partie("etat", 8), self.partie("a", 8), self.partie("b", 8)]
        res = etat.borner(parties, 1000)
        self.assertLessEqual(sum(len(l.encode()) + 1 for l in res), 1000)
        a, b = res.index("--- a ---"), res.index("--- b ---")
        self.assertLessEqual(sum(len(l.encode()) + 1 for l in res[:a - 1]), 400)
        self.assertLessEqual(sum(len(l.encode()) + 1 for l in res[a - 1:b - 1]), 300)
        self.assertEqual(res[a + 1:b - 1], parties[1].lignes[:2])
        self.assertIn("a, 811 octets pour une part de 300 — 6/8 de a", res[-1])

    def test_une_borne_minuscule_reste_tenue(self):
        parties = [self.partie("etat", 2), self.partie("a", 3)]
        for borne in (50, 1):
            res = etat.borner(parties, borne)
            self.assertLessEqual(sum(len(l.encode()) + 1 for l in res), max(borne, 1))

    @staticmethod
    def taille(res: list[str]) -> int:
        return sum(len(l.encode("utf-8")) + 1 for l in res)

    def test_ce_qu_un_groupe_libere_en_coupant_revient_aux_autres_jusqu_a_ce_que_rien_ne_change(self):
        """Un groupe de grosses lignes coupé ne garde rien de ce qui lui
        revient : les autres le reprennent, ceux qui le suivent comme ceux qui
        le précèdent, jusqu'à ce qu'aucune ligne de plus ne tienne."""
        def gros(g: str) -> etat.Partie:
            return etat.Partie(g, [g * 389] * 2, lambda k, t: f"{k}/{t} de {g}",
                               (lambda m, t: ["", f"--- {g} ---"]) if g != "etat" else etat._sans_entete)

        # L'état, le premier, ne garde rien : a, puis b, prennent sa part.
        res = etat.borner([gros("etat"), self.partie("a", 8), self.partie("b", 8)], 1000)
        self.assertLessEqual(self.taille(res), 1000)
        self.assertLess(1000 - self.taille(res), 100)
        a, b = res.index("--- a ---"), res.index("--- b ---")
        self.assertGreater(len(res[a + 1:b - 1]), 3)
        # b, le dernier, ne garde rien : l'état, qui le précède, prend sa part.
        res = etat.borner([self.partie("etat", 8), self.partie("a", 2), gros("b")], 1000)
        self.assertLessEqual(self.taille(res), 1000)
        self.assertLess(1000 - self.taille(res), 100)
        self.assertNotIn("--- b ---", res)
        self.assertEqual(len([l for l in res if l.startswith("etat")]), 5)

    def test_un_groupe_a_deux_parties_coupe_la_seconde_d_abord(self):
        """Le chantier actif public et privé : la seconde partie perd ses
        lignes, puis son en-tête avec la dernière, avant que la première ne
        perde les siennes, et ce qu'un autre groupe libère lui revient dans
        l'ordre inverse ; la ligne de coupe ne dit que les parties coupées."""
        prive = etat.Partie("a", [f"p{i}".ljust(99, ".") for i in range(1, 7)], lambda k, t: f"{k}/{t} de p",
                            lambda m, t: ["", "--- p ---"])
        gros = etat.Partie("b", ["b" * 389] * 2, lambda k, t: f"{k}/{t} de b", lambda m, t: ["", "--- b ---"])
        vus = set()
        for borne in range(300, 1700, 20):
            res = etat.borner([self.partie("etat", 2), self.partie("a", 3), prive, gros], borne)
            self.assertLessEqual(self.taille(res), borne)
            public = [l for l in res if l.startswith("a")]
            privees = [l for l in res if l.startswith("p")]
            self.assertEqual(public, self.partie("a", 3).lignes[:len(public)])
            self.assertEqual(privees, prive.lignes[:len(privees)])
            self.assertEqual("--- p ---" in res, bool(privees))
            self.assertTrue(len(public) == 3 or not privees, (borne, len(public), len(privees)))
            note = res[-1] if res[-1].startswith("!! coupé") else ""
            self.assertEqual("/3 de a" in note, len(public) < 3, borne)
            self.assertEqual("/6 de p" in note, len(privees) < 6, borne)
            vus.add((len(public), len(privees)))
        self.assertIn((3, 6), vus)
        self.assertTrue(any(0 < p < 6 for _, p in vus) and any(0 < a < 3 for a, _ in vus), vus)

    def test_l_etat_perd_d_abord_ce_qui_se_relit_ailleurs_bloc_par_bloc(self):
        """Des blocs insécables, chacun son rang : la coupe retire les rangs
        bas d'abord, chacun depuis la fin ; un en-tête part avec son premier
        élément, un élément avec son lien."""
        lignes = [l.ljust(199, ".") for l in ("en-tête : 2", "  élément 1", "    lien 1", "  élément 2", "    lien 2",
                                              "info", "relu 1", "relu 2")]
        unites, rangs = [3, 2, 1, 1, 1], [etat.ACTION, etat.ACTION, etat.INFO, etat.RELU, etat.RELU]
        partie = etat.Partie("etat", lignes, lambda n, t: f"{n}/{t}", unites=unites,
                             ordre=sorted(range(5), key=lambda k: (rangs[k], -k)))
        # Dans l'ordre de la coupe : relu 2, relu 1, info, l'élément 2 et son
        # lien, puis l'en-tête avec l'élément 1 et son lien.
        possibles = [lignes, lignes[:7], lignes[:6], lignes[:5], lignes[:3], []]
        rangs_vus = []
        with mock.patch.dict(etat.PARTS, {"etat": 1.0}, clear=True):
            for borne in range(1700, 100, -20):
                res = etat.borner([partie], borne)
                self.assertLessEqual(self.taille(res), borne)
                montre = [l for l in res if not l.startswith("!! coupé")]
                self.assertIn(montre, possibles, borne)
                rangs_vus.append(possibles.index(montre))
        self.assertEqual(rangs_vus, sorted(rangs_vus))
        self.assertEqual(set(rangs_vus), set(range(len(possibles))))

    def test_borner_reste_lineaire_sur_un_chantier_actif_de_20000_lignes(self):
        """Les tailles se tiennent bloc par bloc : 20 000 lignes se bornent
        en bien moins d'une seconde (la première correction en prenait 16)."""
        parties = [etat.Partie("etat", ["x" * 60] * 30, lambda n, t: "e"),
                   etat.Partie("a", [f"- ligne {i} " + "y" * 50 for i in range(20000)], lambda n, t: "a",
                               lambda m, t: ["", "--- a ---"]),
                   etat.Partie("b", [f"F-{i:04d} — " + "z" * 60 for i in range(2000)], lambda n, t: "b",
                               lambda m, t: ["", f"--- b {m}/{t} ---"])]
        debut = time.monotonic()
        res = etat.borner(parties, 9500)
        self.assertLess(time.monotonic() - debut, 1.0)
        self.assertLessEqual(self.taille(res), 9500)

    def test_parties_injectees_sans_memoire_lisible_donne_le_chantier_actif_seul(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-parties-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        (racine / "memory").mkdir()
        (racine / "memory/active.md").write_text("# Chantier actif\n\nUne ligne.\n")
        projet = config.Projet(racine=racine)
        (partie,) = etat.parties_injectees(projet, None)
        self.assertEqual((partie.groupe, partie.entete(3, 3), partie.lignes),
                         ("actif", ["", "--- memory/active.md ---"], ["# Chantier actif", "", "Une ligne."]))


class TestRaccourcir(unittest.TestCase):
    def test_raccourcir_coupe_entre_deux_caracteres_et_le_dit(self):
        self.assertEqual(outils.raccourcir("court", 10), "court")
        self.assertEqual(outils.raccourcir("é" * 10, 10), "ééé…")
        self.assertLessEqual(len(outils.raccourcir("x" * 6000, 200).encode("utf-8")), 200)
        self.assertEqual(outils.raccourcir("abcdef", 2), "ab")
        self.assertEqual(etat.ligne_de_titre("F-0001", "t" * 200, " (supposé)"),
                         "F-0001 — " + "t" * (etat.TITRE - 11 - 11 - 3) + "… (supposé)")


class TestCliquetDeLaBorne(unittest.TestCase):
    def test_relever_la_borne_assouplit_la_baisser_durcit(self):
        self.assertEqual(assouplissements({}, {"startup": {"max_bytes": 9500}}), [])
        self.assertEqual(assouplissements({}, {"startup": {"max_bytes": 8000}}), [])
        (cle, pourquoi), = assouplissements({}, {"startup": {"max_bytes": 20000}})
        self.assertEqual((cle, pourquoi), ("startup.max_bytes", "9500 → 20000"))
        self.assertEqual([c for c, _ in assouplissements({"startup": {"max_bytes": 8000}}, {})],
                         ["startup.max_bytes"])


if __name__ == "__main__":
    unittest.main()
