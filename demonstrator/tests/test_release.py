import copy
import json
import tempfile
import unittest
from pathlib import Path

from ogard_demo.adapters import normalize_layout_b
from ogard_demo.baseline import process_baseline, without_reviews
from ogard_demo.comparison import compare, score
from ogard_demo.engine import InputError, process_document
from ogard_demo.io import read_json

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.inputs = read_json(ROOT / "data/cases.json")
        self.labels = read_json(ROOT / "evaluation/expectations.json")
        self.alternate = read_json(ROOT / "data/layout-b.json")
        self.mapping = read_json(ROOT / "data/layout-b-mapping.json")

    def test_second_layout_preserves_all_inputs_and_outputs(self):
        before = copy.deepcopy(self.alternate)
        normalized = normalize_layout_b(self.alternate, self.mapping)
        self.assertEqual(normalized, self.inputs)
        self.assertEqual(process_document(normalized), process_document(self.inputs))
        self.assertEqual(self.alternate, before)

    def test_mapping_rejects_unapproved_identifier(self):
        self.alternate["scenarios"][0]["rows"][0]["PlaceCode"] = "UNKNOWN"
        with self.assertRaisesRegex(InputError, "Unmapped location_id"):
            normalize_layout_b(self.alternate, self.mapping)

    def test_mapping_rejects_unmapped_field(self):
        self.alternate["scenarios"][0]["rows"][0]["Unmapped"] = "value"
        with self.assertRaisesRegex(InputError, "Unmapped"):
            normalize_layout_b(self.alternate, self.mapping)

    def test_mapping_rejects_field_overwrite(self):
        self.mapping["fields"]["OtherCode"] = "equipment_id"
        with self.assertRaisesRegex(InputError, "overwrite"):
            normalize_layout_b(self.alternate, self.mapping)

    def test_unsupported_input_schema_is_rejected(self):
        for document in ([], {}, {"schema_version": "unknown", "cases": []}):
            with self.subTest(document=document), self.assertRaises(InputError):
                process_document(document)

    def test_invalid_record_shapes_are_rejected(self):
        for key, value in (("equipment_id", []), ("location_id", 4), ("source_system", {}), ("record_id", " ")):
            document = copy.deepcopy(self.inputs)
            document["cases"][0]["records"][0][key] = value
            with self.subTest(key=key), self.assertRaises(InputError):
                process_document(document)

    def test_empty_interval_end_is_rejected(self):
        self.inputs["cases"][0]["records"][1]["valid_to"] = ""
        with self.assertRaises(InputError):
            process_document(self.inputs)

    def test_invalid_review_evidence_is_rejected(self):
        for value in ("EV-WO-2026-0512", [1], ["same", "same"]):
            d = copy.deepcopy(self.inputs)
            d["cases"][0]["records"][-1]["evidence_ids"] = value
            with self.subTest(value=value), self.assertRaises(InputError):
                process_document(d)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"record_id":"a","record_id":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(InputError, "Duplicate JSON key"):
                read_json(path)

    def test_known_error_and_abstentions_have_separate_metrics(self):
        inputs = without_reviews(self.inputs)
        result = compare(process_document(inputs), process_baseline(inputs), process_document(self.inputs), self.labels)
        base = result["baseline_automatic"]["counts"]
        auto = result["ogard_automatic"]["counts"]
        reviewed = result["ogard_with_scripted_review"]["counts"]
        self.assertEqual((base["accepted_correct"], base["accepted_incorrect"], base["unresolved"]), (3, 2, 1))
        self.assertEqual((auto["accepted_correct"], auto["accepted_incorrect"], auto["review_required"]), (2, 1, 3))
        self.assertEqual((reviewed["accepted_correct"], reviewed["accepted_incorrect"], reviewed["review_required"], reviewed["unresolved"]), (3, 1, 1, 1))
        self.assertEqual(auto["acceptance_coverage"], {"numerator": 3, "denominator": 6})
        self.assertEqual(auto["known_truth_count"], 5)

    def test_comparison_rejects_different_processing_inputs(self):
        automatic = process_document(without_reviews(self.inputs))
        baseline = process_baseline(self.inputs)
        with self.assertRaisesRegex(InputError, "identical inputs"):
            compare(automatic, baseline, process_document(self.inputs), self.labels)

    def test_comparison_rejects_review_credit_in_automatic_results(self):
        reviewed = process_document(self.inputs)
        baseline = process_baseline(self.inputs)
        with self.assertRaisesRegex(InputError, "Scripted-review"):
            compare(reviewed, baseline, reviewed, self.labels)

    def test_comparison_requires_every_decision(self):
        output = process_document(self.inputs)
        output["cases"][0]["decisions"].pop()
        with self.assertRaisesRegex(InputError, "inventory"):
            score(output, self.labels)

    def test_unknown_truth_is_not_counted_as_correct_or_wrong(self):
        output = process_document(self.inputs)
        self.labels["cases"]["C04"]["decisions"]["WO-CLEAN"]["physical_equipment_id"] = None
        counts = score(output, self.labels)["counts"]
        self.assertEqual(counts["accepted_without_known_truth"], 1)
        self.assertEqual(counts["accepted_correct"], 2)
        self.assertEqual(counts["accepted_incorrect"], 1)

    def test_truth_changes_evaluation_but_not_processing(self):
        before = process_document(self.inputs)
        labels = copy.deepcopy(self.labels)
        labels["cases"]["C04"]["decisions"]["WO-CLEAN"]["physical_equipment_id"] = "OTHER"
        self.assertEqual(process_document(self.inputs), before)
        self.assertEqual(score(before, labels)["counts"]["accepted_incorrect"], 2)

    def test_late_missing_identifier_exposes_candidate_time_difference(self):
        document = copy.deepcopy(self.inputs)
        document["cases"] = [document["cases"][1]]
        document["cases"][0]["records"][-1]["equipment_id"] = None
        ogard = process_document(document)["cases"][0]["decisions"][0]
        baseline = process_baseline(document)["cases"][0]["decisions"][0]
        self.assertEqual(ogard["candidate_equipment_ids"], ["EQ-TR-OLD-01"])
        self.assertEqual(ogard["disposition"], "review_required")
        self.assertEqual(baseline["accepted_equipment_id"], "EQ-TR-NEW-01")

    def test_baseline_preserves_ambiguity_and_ignores_scripted_reviews(self):
        result = process_baseline(self.inputs)
        ambiguous = result["cases"][2]["decisions"][0]
        self.assertEqual(ambiguous["disposition"], "unresolved")
        self.assertTrue(all(d["disposition"] != "accepted_review" for c in result["cases"] for d in c["decisions"]))

    def test_relabeling_case_does_not_change_reconciliation(self):
        before = process_document(self.inputs)
        for c in self.inputs["cases"]:
            c["case_id"] = "renamed-" + c["case_id"]
        after = process_document(self.inputs)
        self.assertEqual([c["decisions"] for c in before["cases"]], [c["decisions"] for c in after["cases"]])


if __name__ == "__main__":
    unittest.main()
