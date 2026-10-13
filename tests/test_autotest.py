import os
import unittest

from socle import autotest, verification


class TestAttribution(unittest.TestCase):
    """L'auto-test ne compte un défaut comme attrapé que par le contrôle
    attendu : le rapport nomme TOUS les contrôles, réussis compris."""

    def cas(self, controle):
        return autotest.Cas("x", "x", "git", controle, None)

    def test_seule_la_synthese_compte(self):
        sortie = "  docs.valeurs    ok\n  memoire.budgets   ECHEC\n\nECHEC — 1 contrôle(s) : memoire.budgets"
        self.assertTrue(autotest._attrape_par(self.cas("memoire.budgets"), sortie))
        self.assertFalse(autotest._attrape_par(self.cas("docs.valeurs"), sortie))

    def test_un_controle_que_le_hook_nomme_aussi_s_attrape_en_ci(self):
        """B-0044, L4 : `memoire.preuves` n'était compté attrapé que par la
        phrase du refus du hook ; le même défaut, commité, passait pour muet."""
        sortie = "  memoire.preuves   ECHEC\n\nECHEC — 1 contrôle(s) : memoire.preuves"
        self.assertTrue(autotest._attrape_par(self.cas("memoire.preuves"), sortie))
        self.assertFalse(autotest._attrape_par(self.cas("memoire.preuves"), "ECHEC — 1 contrôle(s) : docs.valeurs"))

    def test_raison_du_hook_de_l_agent(self):
        self.assertTrue(autotest._attrape_par(self.cas("anti-fabrication"), "SHA fabriqué : abc…"))
        self.assertFalse(autotest._attrape_par(self.cas("anti-fabrication"), "autre raison"))


class TestCouverture(unittest.TestCase):
    """B-0044, L4 : huit contrôles sur trente-trois n'avaient aucun défaut
    injecté, et un garde-fou qu'on n'a jamais vu échouer ne prouve rien."""

    def test_chaque_controle_a_son_defaut_injecte_ou_sa_raison(self):
        from socle import contexte

        couverts = {c.controle for c in autotest._cas()}
        self.assertEqual(sorted(set(contexte.charger_controles()) - couverts - set(autotest.SANS_DEFAUT)), [])
        self.assertTrue(all(raison.strip() for raison in autotest.SANS_DEFAUT.values()))

    def test_chaque_refus_reconnu_a_son_defaut_injecte(self):
        couverts = {c.controle for c in autotest._cas()}
        self.assertEqual(sorted(set(autotest.RAISONS_AGENT) - couverts), [])


class TestAtelierPartage(unittest.TestCase):
    """L6 : les cas tournent sur plusieurs fils ; une origine privée se
    prépare une fois, et chaque clone a son propre dossier."""

    def test_une_origine_privee_se_prepare_une_fois_sur_plusieurs_fils(self):
        from concurrent.futures import ThreadPoolExecutor
        from pathlib import Path

        import socle

        a = autotest.Atelier(Path(socle.__file__).resolve().parent.parent, False)
        self.addCleanup(a.nettoyer)
        a.preparer()
        with ThreadPoolExecutor(max_workers=4) as fils:
            origines = list(fils.map(lambda _: a.origine_privee("chiffre"), range(4)))
            clones = list(fils.map(lambda _: a.clone(), range(4)))
        self.assertEqual(len(set(origines)), 1)
        self.assertEqual(len(set(clones)), 4)
        self.assertTrue((origines[0] / "memory/private/canonical.md").is_file())


AUTOTEST_ENSUITE = bool(os.environ.get(autotest.ENSUITE))
ETAPES_RAPIDES = bool(os.environ.get(verification.RAPIDE))


class TestInjection(unittest.TestCase):
    # `socle ci` lance l'auto-test lui-même, juste après la suite de tests :
    # il ne tourne pas deux fois (L6). Trop long pour une fin de tour, il
    # attend la CI (D-0019).
    @unittest.skipIf(AUTOTEST_ENSUITE, "lancé juste après par la même CI, qui ne le joue pas deux fois")
    @unittest.skipIf(ETAPES_RAPIDES, "trop long pour une fin de tour : la CI le joue à chaque push")
    def test_chaque_defaut_est_attrape_et_chaque_temoin_passe(self):
        rapport = autotest.executer()
        self.assertTrue(rapport.reussi, rapport.texte())
        # Depuis le jalon 7, aucun défaut du cadrage n'est déclaré non couvert.
        self.assertEqual([c.controle for c in rapport.constats if c.gravite == "indisponible"], [])


if __name__ == "__main__":
    unittest.main()
