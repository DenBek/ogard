import copy
import json
import unittest
from pathlib import Path

from ogard_demo.engine import InputError, process_case, process_document
from ogard_demo.evaluate import evaluate_document

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.inputs = json.loads((ROOT / "data/cases.json").read_text())
        self.expected = json.loads((ROOT / "evaluation/expectations.json").read_text())

    def case(self, index=0):
        return copy.deepcopy(self.inputs["cases"][index])

    def test_original_review_preserves_telemetry_conflict(self):
        result = process_case(self.case())
        outcomes = {d["subject_record_id"]: d for d in result["decisions"]}
        self.assertEqual(outcomes["EV-WO-2026-0512"]["disposition"], "accepted_review")
        self.assertEqual(outcomes["EV-HIST-TX2-OIL"]["disposition"], "review_required")
        self.assertEqual(outcomes["EV-HIST-TX2-OIL"]["contradictions"][0]["code"], "TELEMETRY_EQUIPMENT_CONFLICT")

    def test_no_future_evidence_in_earlier_decision(self):
        result = process_case(self.case())
        first = next(a for a in result["audit"] if a["event"] == "decision_updated")
        self.assertEqual(first["decision"]["disposition"], "unresolved")
        self.assertEqual(first["decision"]["evidence_ids"], ["EV-WO-2026-0512"])
        self.assertEqual(first["processed_at"], "2026-05-12T10:02:15Z")

    def test_late_arrival_uses_event_time(self):
        d = process_case(self.case(1))["decisions"][0]
        self.assertEqual(d["accepted_equipment_id"], "EQ-TR-OLD-01")

    def test_exact_replacement_boundary_is_new_installation(self):
        c = self.case(1)
        q = c["records"][-1]
        q["event_at"] = "2026-04-15T00:00:00Z"
        q["equipment_id"] = "EQ-TR-NEW-01"
        d = process_case(c)["decisions"][0]
        self.assertEqual(d["candidate_equipment_ids"], ["EQ-TR-NEW-01"])
        self.assertEqual(d["disposition"], "accepted_automatic")

    def test_timezone_equivalent_boundary(self):
        c = self.case(1)
        c["records"][-1]["event_at"] = "2026-04-14T20:00:00-04:00"
        c["records"][-1]["equipment_id"] = "EQ-TR-NEW-01"
        self.assertEqual(process_case(c)["decisions"][0]["candidate_equipment_ids"], ["EQ-TR-NEW-01"])

    def test_competing_histories_do_not_force_match(self):
        d = process_case(self.case(2))["decisions"][0]
        self.assertEqual(d["disposition"], "unresolved")
        self.assertIsNone(d["accepted_equipment_id"])
        self.assertEqual(len(d["candidate_equipment_ids"]), 2)

    def test_wrong_review_role_is_rejected(self):
        c = self.case()
        c["records"][-1]["role"] = "telemetry_owner"
        with self.assertRaisesRegex(InputError, "role not authorized"):
            process_case(c)

    def test_review_cannot_accept_unsupported_equipment(self):
        c = self.case()
        c["records"][-1]["equipment_id"] = "EQ-UNSUPPORTED"
        with self.assertRaisesRegex(InputError, "not supported"):
            process_case(c)

    def test_review_cannot_cite_future_evidence(self):
        c = self.case()
        c["records"][-1]["evidence_ids"].append("FUTURE-INSTALLATION")
        future = copy.deepcopy(c["records"][2])
        future.update(record_id="FUTURE-INSTALLATION", received_at="2026-05-13T00:00:00Z")
        c["records"].append(future)
        with self.assertRaisesRegex(InputError, "unavailable evidence"):
            process_case(c)

    def test_later_conflicting_evidence_reopens_review(self):
        c = self.case()
        conflicting = copy.deepcopy(c["records"][2])
        conflicting.update(record_id="LATE-CONFLICT", equipment_id="EQ-OTHER", received_at="2026-05-12T11:00:00Z")
        c["records"].append(conflicting)
        result = process_case(c)
        d = next(d for d in result["decisions"] if d["subject_record_id"] == "EV-WO-2026-0512")
        self.assertEqual(d["reason_code"], "EVIDENCE_CHANGED_SINCE_REVIEW")
        self.assertIsNone(d["accepted_equipment_id"])
        history = [a["decision"]["disposition"] for a in result["audit"] if a["event"] == "decision_updated" and a["subject_record_id"] == "EV-WO-2026-0512"]
        self.assertIn("accepted_review", history)
        self.assertEqual(history[-1], "review_required")

    def test_input_is_preserved_and_execution_is_deterministic(self):
        before = copy.deepcopy(self.inputs)
        first = process_document(self.inputs)
        self.assertEqual(self.inputs, before)
        self.assertEqual(first, process_document(self.inputs))

    def test_invalid_identifiers_and_timestamps_fail_explicitly(self):
        for change in ("duplicate", "timezone", "interval"):
            with self.subTest(change=change):
                c = self.case(3)
                if change == "duplicate":
                    c["records"].append(copy.deepcopy(c["records"][0]))
                elif change == "timezone":
                    c["records"][-1]["event_at"] = "2026-05-12T09:00:00"
                else:
                    c["records"][0]["valid_to"] = "2019-01-01T00:00:00Z"
                with self.assertRaises(InputError):
                    process_case(c)

    def test_shared_error_is_counted_as_wrong_automatic_accept(self):
        evaluation = evaluate_document(process_document(self.inputs), self.expected)
        self.assertEqual(evaluation["automatic_accepts"], 3)
        self.assertEqual(evaluation["incorrect_automatic_accepts"], 1)
        self.assertFalse(evaluation["cases"][-1]["accepted_mapping_truth_checks"][0]["agrees_with_hidden_truth"])

    def test_evaluation_detects_modified_audit(self):
        result = process_document(self.inputs)
        result["cases"][0]["audit"][0]["source_hash"] = "altered"
        self.assertFalse(evaluate_document(result, self.expected)["all_workflow_checks_passed"])

    def test_all_inputs_are_accounted_for_and_declared_checks_pass(self):
        evaluation = evaluate_document(process_document(self.inputs), self.expected)
        self.assertTrue(evaluation["all_workflow_checks_passed"])
        self.assertEqual(evaluation["scripted_review_accepts"], 1)


if __name__ == "__main__":
    unittest.main()
