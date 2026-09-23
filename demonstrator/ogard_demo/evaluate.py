"""Post-processing evaluation; hidden labels are used only here."""

from .engine import digest, instant


def evaluate_document(processed, expected):
    observed_ids = {case["case_id"] for case in processed["cases"]}
    if observed_ids != set(expected["cases"]):
        raise ValueError("Observed and expected case identifiers differ")
    results = []
    automatic = wrong_automatic = reviewed = 0
    for case in processed["cases"]:
        labels = expected["cases"][case["case_id"]]
        actual = {d["subject_record_id"]: d for d in case["decisions"]}
        checks = []
        truth = []
        checks.append({"name": "decision_inventory", "passed": set(actual) == set(labels["decisions"])})
        for sid, target in labels["decisions"].items():
            got = actual.get(sid, {})
            passed = (got.get("disposition") == target["disposition"]
                      and got.get("accepted_equipment_id") == target["accepted_equipment_id"]
                      and sorted(c["code"] for c in got.get("contradictions", [])) == sorted(target["contradiction_codes"]))
            checks.append({"name": "declared_behavior:" + sid, "passed": passed})
            if got.get("disposition") in ("accepted_automatic", "accepted_review"):
                correct = got["accepted_equipment_id"] == target["physical_equipment_id"]
                truth.append({"subject_record_id": sid, "accepted_equipment_id": got["accepted_equipment_id"],
                              "hidden_physical_equipment_id": target["physical_equipment_id"],
                              "agrees_with_hidden_truth": correct, "mode": got["disposition"]})
                if got["disposition"] == "accepted_automatic":
                    automatic += 1
                    wrong_automatic += int(not correct)
                else:
                    reviewed += 1
        sources = {r["record_id"]: r for r in case["source_records"]}
        ledger = case["input_ledger"]
        checks.append({"name": "input_accounting", "passed": len(ledger) == len(sources)
                       and {row["record_id"] for row in ledger} == set(sources)})
        prior_hash, available, audit_ok, snapshots = None, set(), True, {}
        for index, entry in enumerate(case["audit"], 1):
            body = {key: value for key, value in entry.items() if key != "entry_hash"}
            audit_ok &= entry["sequence"] == index and entry["previous_hash"] == prior_hash and digest(body) == entry["entry_hash"]
            trigger = sources.get(entry["trigger_record_id"])
            audit_ok &= bool(trigger) and entry["processed_at"] == trigger["received_at"]
            if entry["event"] == "source_received":
                audit_ok &= entry["trigger_record_id"] not in available and entry["source_hash"] == digest(trigger)
                available.add(entry["trigger_record_id"])
            elif entry["event"] == "decision_updated":
                d = entry["decision"]
                audit_ok &= set(d["evidence_ids"]).issubset(available)
                audit_ok &= all(instant(sources[s]["received_at"]) <= instant(entry["processed_at"]) for s in d["evidence_ids"] if s in sources)
                sid = entry["subject_record_id"]
                audit_ok &= entry["supersedes_sequence"] == snapshots.get(sid, (None, None))[0]
                snapshots[sid] = (entry["sequence"], d)
            else:
                audit_ok = False
            prior_hash = entry["entry_hash"]
        audit_ok &= available == set(sources)
        audit_ok &= {sid: d for sid, (_, d) in snapshots.items()} == actual
        checks.append({"name": "audit_integrity_and_evidence_availability", "passed": bool(audit_ok)})
        results.append({"case_id": case["case_id"], "checks": checks,
                        "all_workflow_checks_passed": all(c["passed"] for c in checks),
                        "accepted_mapping_truth_checks": truth, "interpretation": labels["interpretation"]})
    return {"evaluation_version": "ogard-demo-evaluator-1", "expectations_hash": digest(expected),
            "case_count": len(results), "all_workflow_checks_passed": all(r["all_workflow_checks_passed"] for r in results),
            "automatic_accepts": automatic, "incorrect_automatic_accepts": wrong_automatic,
            "scripted_review_accepts": reviewed,
            "interpretation": "Selected illustrative cases, not a representative benchmark. The shared-source error counts as an incorrect automatic acceptance even though it is the expected limitation of the workflow.",
            "independent_reproduction": "not_performed", "cases": results}
