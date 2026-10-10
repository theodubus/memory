import unittest

from socle.controles_cliquet import assouplissements

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
