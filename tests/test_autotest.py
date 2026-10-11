import unittest

from socle import autotest


class TestAttribution(unittest.TestCase):
    """L'auto-test ne compte un défaut comme attrapé que par le contrôle
    attendu : le rapport nomme TOUS les contrôles, réussis compris."""

    def cas(self, controle):
        return autotest.Cas("x", "x", "git", controle, None)

    def test_seule_la_synthese_compte(self):
        sortie = "  docs.valeurs    ok\n  memoire.budgets   ECHEC\n\nECHEC — 1 contrôle(s) : memoire.budgets"
        self.assertTrue(autotest._attrape_par(self.cas("memoire.budgets"), sortie))
        self.assertFalse(autotest._attrape_par(self.cas("docs.valeurs"), sortie))

    def test_raison_du_hook_de_l_agent(self):
        self.assertTrue(autotest._attrape_par(self.cas("anti-fabrication"), "SHA fabriqué : abc…"))
        self.assertFalse(autotest._attrape_par(self.cas("anti-fabrication"), "autre raison"))


class TestInjection(unittest.TestCase):
    def test_chaque_defaut_est_attrape_et_chaque_temoin_passe(self):
        rapport = autotest.executer()
        self.assertTrue(rapport.reussi, rapport.texte())
        # Depuis le jalon 7, aucun défaut du cadrage n'est déclaré non couvert.
        self.assertEqual([c.controle for c in rapport.constats if c.gravite == "indisponible"], [])


if __name__ == "__main__":
    unittest.main()
