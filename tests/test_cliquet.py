import unittest

from socle.checks_ratchet import assouplissements

BASE = {
    "budgets": {"memoire/actif.md": {"max_bytes": 6000}},
    "staleness": {"active_days": 7},
    "nocopy": {"min_chars": 200, "exclude": []},
    "memory": {"require_update_on_code_change": True},
    "mutation": {"caps": {"src/a.rs": {"max": 3, "reason": "équivalents"}}},
    "docmap": [{"code": ["src/**"], "docs": ["docs/a.md"]}],
    "values": [{"name": "n", "file": "src/a.rs", "regex": "N = (\\d+)"}],
}


def changer(**modifs):
    import copy

    d = copy.deepcopy(BASE)
    for chemin, v in modifs.items():
        noeud = d
        cles = chemin.split("__")
        for k in cles[:-1]:
            noeud = noeud[k]
        noeud[cles[-1]] = v
    return d


class TestCliquet(unittest.TestCase):
    def test_rien_ne_change(self):
        self.assertEqual(assouplissements(BASE, BASE), [])

    def test_durcir_est_libre(self):
        apres = changer(staleness__active_days=3, nocopy__min_chars=100)
        apres["budgets"]["memoire/actif.md"]["max_bytes"] = 5000
        apres["budgets"]["AGENTS.md"] = {"max_bytes": 9000}
        apres["docmap"].append({"code": ["tests/**"], "docs": ["docs/t.md"]})
        self.assertEqual(assouplissements(BASE, apres), [])

    def test_budget_releve(self):
        apres = changer()
        apres["budgets"]["memoire/actif.md"]["max_bytes"] = 9000
        (cle, pourquoi), = assouplissements(BASE, apres)
        self.assertEqual(cle, 'budgets."memoire/actif.md".max_bytes')
        self.assertIn("6000 → 9000", pourquoi)

    def test_plafond_de_mutation_releve_ou_retire(self):
        neuf = changer()
        neuf["mutation"]["caps"]["src/b.rs"] = {"max": 0}
        self.assertEqual(assouplissements(BASE, neuf), [])  # un module de plus dans le cliquet : durcit
        releve = changer()
        releve["mutation"]["caps"]["src/a.rs"]["max"] = 5
        self.assertEqual([c for c, _ in assouplissements(BASE, releve)], ['mutation.caps."src/a.rs".max'])
        retire = changer()
        del retire["mutation"]["caps"]["src/a.rs"]
        self.assertTrue(assouplissements(BASE, retire, modules_existants={"src/a.rs"}))
        self.assertEqual(assouplissements(BASE, retire, modules_existants=set()), [])

    def test_le_budget_d_un_fichier_disparu_se_retire(self):
        # ADR-0025 : le backlog en un fichier devient un dossier, et le
        # budget du fichier unique part avec lui ; celui d'un fichier qui
        # existe ne se retire pas.
        retire = changer()
        del retire["budgets"]["memoire/actif.md"]
        self.assertTrue(assouplissements(BASE, retire, modules_existants={"memoire/actif.md"}))
        self.assertEqual(assouplissements(BASE, retire, modules_existants={"memoire/autre.md"}), [])

    def test_un_module_a_mesurer_puis_mesure(self):
        """B-0034, P1 : un module « à mesurer » entre au cliquet sans
        l'assouplir ; recevoir son plafond le durcit ; un module mesuré remis
        « à mesurer » perd son plafond, ce qui assouplit."""
        a_mesurer = changer()
        a_mesurer["mutation"]["caps"]["src/b.rs"] = {"pending": True}
        self.assertEqual(assouplissements(BASE, a_mesurer), [])
        mesure = changer()
        mesure["mutation"]["caps"]["src/b.rs"] = {"max": 2, "reason": "mesuré le 2026-10-12 : 2 survivant(s)"}
        self.assertEqual(assouplissements(a_mesurer, mesure), [])
        remis = changer()
        remis["mutation"]["caps"]["src/a.rs"] = {"pending": True}
        self.assertEqual([c for c, _ in assouplissements(BASE, remis, modules_existants={"src/a.rs"})],
                         ['mutation.caps."src/a.rs".max'])
        repasse = changer()
        repasse["mutation"]["caps"]["src/b.rs"] = {"pending": False}
        self.assertEqual([c for c, _ in assouplissements(repasse, a_mesurer)], ['mutation.caps."src/b.rs".pending'])

    def test_un_plafond_ecrit_a_la_main(self):
        """B-0044, L2 : un module « à mesurer » recevait n'importe quel
        plafond écrit à la main, que le cliquet prenait pour un durcissement."""
        a_mesurer = changer()
        a_mesurer["mutation"]["caps"]["src/b.rs"] = {"pending": True}
        invente = changer()
        invente["mutation"]["caps"]["src/b.rs"] = {"max": 40, "reason": "mesuré"}
        self.assertEqual([c for c, _ in assouplissements(a_mesurer, invente)], ['mutation.caps."src/b.rs".max'])
        faux_compte = changer()
        faux_compte["mutation"]["caps"]["src/b.rs"] = {"max": 40, "reason": "mesuré le 2026-10-12 : 2 survivant(s)"}
        self.assertTrue(assouplissements(a_mesurer, faux_compte))
        nul = changer()
        nul["mutation"]["caps"]["src/b.rs"] = {"max": 0}
        self.assertEqual(assouplissements(a_mesurer, nul), [])

    def test_docs_ajoutees_a_une_correspondance(self):
        """B-0044, L2 : une doc de plus dans une correspondance rend son
        exigence plus facile à satisfaire ; une correspondance de plus sur le
        même code la durcit."""
        elargie = changer()
        elargie["docmap"][0]["docs"].append("README.md")
        (cle, pourquoi), = assouplissements(BASE, elargie)
        self.assertEqual(cle, 'docmap "src/**"')
        self.assertIn("README.md", pourquoi)
        doublee = changer()
        doublee["docmap"].append({"code": ["src/**"], "docs": ["docs/b.md"]})
        self.assertEqual(assouplissements(BASE, doublee), [])
        resserree = changer()
        resserree["docmap"][0]["docs"] = []
        self.assertEqual(assouplissements(BASE, resserree), [])

    def test_exclusion_ajoutee_et_booleen_desactive(self):
        apres = changer(nocopy__exclude=["docs/**"], memory__require_update_on_code_change=False)
        cles = sorted(c for c, _ in assouplissements(BASE, apres))
        self.assertEqual(cles, ["memory.require_update_on_code_change", "nocopy.exclude"])

    def test_correspondance_et_valeur_retirees(self):
        apres = changer(docmap=[], values=[])
        cles = [c for c, _ in assouplissements(BASE, apres)]
        self.assertEqual(cles, ['docmap "src/**"', 'values "n"'])

    def test_cle_inconnue_signalee(self):
        apres = changer()
        apres["regression"] = {"fix_subject": "^jamais$"}
        self.assertEqual([c for c, _ in assouplissements(BASE, apres)], ["regression.fix_subject"])


if __name__ == "__main__":
    unittest.main()
