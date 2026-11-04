from django.test import SimpleTestCase

from core import policy_lab as lab


def _panel(catch: float, *, correlation: float = 0.0, roles: int = 1) -> lab.Panel:
    reviewers = tuple(
        lab.Reviewer(role=lab.ROLES[i], catches={"unsupported_claim": catch}, false_object=0.0)
        for i in range(roles)
    )
    return lab.Panel(id="t", reviewers=reviewers, correlation=correlation)


def _scenario() -> lab.Scenario:
    return lab.Scenario(
        "s1", "planted claim", "standard", (lab.Defect("d1", "unsupported_claim", 3),)
    )


NO_OBJECTION = lab.Policy(
    "p",
    (
        lab.Rule("auto_publish", max_objections=0),
        lab.Rule("queue_human", max_objections=99),
    ),
)


class RuleTests(SimpleTestCase):
    def test_first_matching_rule_decides(self):
        policy = lab.Policy(
            "p",
            (
                lab.Rule("auto_publish", frozenset({"cosmetic"}), max_objections=0),
                lab.Rule("queue_human", max_objections=99),
            ),
        )
        self.assertEqual(policy.decide("cosmetic", 0, 3), "auto_publish")
        self.assertEqual(policy.decide("cosmetic", 1, 3), "queue_human")
        self.assertEqual(policy.decide("high", 0, 3), "queue_human")

    def test_no_matching_rule_blocks(self):
        policy = lab.Policy("p", (lab.Rule("auto_publish", frozenset({"low"}), max_objections=0),))
        self.assertEqual(policy.decide("high", 0, 3), "block")

    def test_min_reviews_is_enforced(self):
        policy = lab.Policy("p", (lab.Rule("auto_publish", max_objections=0, min_reviews=3),))
        self.assertEqual(policy.decide("low", 0, 2), "block")
        self.assertEqual(policy.decide("low", 0, 3), "auto_publish")

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            lab.Rule("publish_everything")

    def test_unknown_defect_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            lab.Defect("d1", "vibes", 1)

    def test_unknown_risk_class_is_rejected(self):
        with self.assertRaises(ValueError):
            lab.Scenario("s", "t", "spicy")


class SimulationTests(SimpleTestCase):
    def test_clean_edit_never_escapes(self):
        report = lab.run_lab([lab.Scenario("clean", "clean", "low")], _panel(0.0), [NO_OBJECTION], trials=50)
        cell = report.cell("p", "low")
        self.assertEqual(cell.escaped, 0)
        self.assertEqual(cell.publish_rate, 1.0)

    def test_blind_panel_publishes_every_defect(self):
        report = lab.run_lab([_scenario()], _panel(0.0), [NO_OBJECTION], trials=50)
        cell = report.cell("p", "standard")
        self.assertEqual(cell.escape_rate, 1.0)

    def test_certain_reviewer_catches_every_defect(self):
        report = lab.run_lab([_scenario()], _panel(1.0), [NO_OBJECTION], trials=50)
        cell = report.cell("p", "standard")
        self.assertEqual(cell.escaped, 0)
        self.assertEqual(cell.queued, 50)

    def test_false_objection_sends_clean_edit_to_human(self):
        panel = lab.Panel(
            id="t",
            reviewers=(lab.Reviewer(role="fact_check", catches={}, false_object=1.0),),
        )
        report = lab.run_lab([lab.Scenario("clean", "clean", "low")], panel, [NO_OBJECTION], trials=20)
        self.assertEqual(report.cell("p", "low").queued, 20)

    def test_correlation_reduces_ensemble_recall(self):
        independent = lab.run_lab([_scenario()], _panel(0.5, correlation=0.0, roles=2), [NO_OBJECTION], trials=800)
        correlated = lab.run_lab([_scenario()], _panel(0.5, correlation=1.0, roles=2), [NO_OBJECTION], trials=800)
        self.assertGreater(independent.cell("p", "standard").recall("unsupported_claim"), 0.65)
        self.assertLess(correlated.cell("p", "standard").recall("unsupported_claim"), 0.60)

    def test_human_all_queues_everything(self):
        policy = lab.Policy("h", (lab.Rule("queue_human", max_objections=99),))
        report = lab.run_lab([_scenario()], _panel(0.0), [policy], trials=30)
        cell = report.cell("h", "standard")
        self.assertEqual(cell.human_load_per_100, 100.0)
        self.assertEqual(cell.escaped, 0)

    def test_audit_sampling_is_applied(self):
        policy = lab.Policy(
            "a",
            (lab.Rule("publish_with_audit", max_objections=99),),
            audit_sample=0.5,
        )
        report = lab.run_lab([_scenario()], _panel(0.0), [policy], trials=400)
        audited = report.cell("a", "standard").audited
        self.assertGreater(audited, 150)
        self.assertLess(audited, 250)


class ReportTests(SimpleTestCase):
    def test_report_is_deterministic_for_a_seed(self):
        first = lab.run_lab(lab.scenarios()[:3], lab.panels()["weak"], lab.policies(), trials=20, seed=3)
        second = lab.run_lab(lab.scenarios()[:3], lab.panels()["weak"], lab.policies(), trials=20, seed=3)
        self.assertEqual(first.to_json(), second.to_json())

    def test_report_json_is_stable_and_serialisable(self):
        report = lab.run_lab(lab.scenarios()[:2], lab.panels()["mixed"], lab.policies()[:2], trials=5)
        payload = report.as_dict()
        self.assertEqual(payload["panel"], "mixed")
        self.assertTrue(payload["cells"])
        for cell in payload["cells"]:
            self.assertIn("escape_rate", cell)
            self.assertIn("human_load_per_100", cell)

    def test_best_cell_ignores_empty_risk_classes(self):
        report = lab.run_lab([_scenario()], _panel(1.0), [NO_OBJECTION], trials=10)
        self.assertIsNone(report.best_cell("high"))
        self.assertIsNotNone(report.best_cell("standard"))

    def test_stricter_policy_never_escapes_more(self):
        report = lab.run_lab(lab.scenarios(), lab.panels()["weak"], lab.policies(), trials=60)
        by_policy = {p: sum(c.escaped for c in report.cells if c.policy_id == p) for p in
                     ("human-all", "tiered", "low-risk-audit", "no-objection")}
        self.assertEqual(by_policy["human-all"], 0)
        self.assertLessEqual(by_policy["tiered"], by_policy["no-objection"])

    def test_fingerprint_is_short_and_stable(self):
        report = lab.run_lab(lab.scenarios()[:1], lab.panels()["weak"], lab.policies()[:1], trials=5)
        self.assertEqual(len(lab.fingerprint(report)), 12)
        self.assertEqual(lab.fingerprint(report), lab.fingerprint(report))


class LabViewTests(__import__('django.test', fromlist=['TestCase']).TestCase):
    def setUp(self):
        import json, tempfile
        from pathlib import Path
        from django.test import override_settings
        from django.conf import settings
        from core import policy_lab as lab

        self._tmp = tempfile.TemporaryDirectory()
        runtime = Path(self._tmp.name)
        (runtime / 'lab').mkdir()
        report = lab.run_lab(lab.scenarios()[:3], lab.panels()['mixed'], lab.policies()[:2], trials=5)
        payload = report.as_dict()
        payload['generated_at'] = '2026-11-04T00:00:00+00:00'
        payload['panels'] = [dict(payload, fingerprint='abc123', recommended={'standard': 'no-objection'})]
        payload['policies'] = ['human-all', 'no-objection']
        (runtime / 'lab' / 'latest.json').write_text(json.dumps(payload))
        self._settings = override_settings(GALACTICA={**settings.GALACTICA, 'RUNTIME_DIR': runtime})
        self._settings.enable()

    def tearDown(self):
        self._settings.disable()
        self._tmp.cleanup()

    def test_lab_page_renders_the_report(self):
        response = self.client.get('/lab/', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Policy lab')
        self.assertContains(response, 'no-objection')
        self.assertContains(response, 'human / 100')

    def test_lab_page_without_a_report_asks_for_a_run(self):
        import shutil
        from pathlib import Path
        from django.conf import settings
        shutil.rmtree(Path(settings.GALACTICA['RUNTIME_DIR']) / 'lab')
        response = self.client.get('/lab/', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No report yet')
        self.assertContains(response, 'run_policy_lab')
