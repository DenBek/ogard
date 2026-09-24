"""Post-processing metrics; withheld truth is read only after decisions exist."""

from .engine import InputError, digest


def score(processed, expected):
    expected_cases = expected["cases"]
    if len(processed["cases"]) != len(expected_cases) or {c["case_id"] for c in processed["cases"]} != set(expected_cases):
        raise InputError("Comparison case inventory differs")
    counts = {key: 0 for key in ("decision_count", "known_truth_count", "accepted", "accepted_correct",
                                 "accepted_incorrect", "accepted_without_known_truth", "review_required",
                                 "unresolved", "rejected")}
    rows = []
    for case in processed["cases"]:
        targets = expected_cases[case["case_id"]]["decisions"]
        if len(case["decisions"]) != len(targets) or {d["subject_record_id"] for d in case["decisions"]} != set(targets):
            raise InputError("Comparison decision inventory differs")
        for decision in case["decisions"]:
            target = targets[decision["subject_record_id"]]
            truth = target["physical_equipment_id"]
            disposition = decision["disposition"]
            equipment = decision["accepted_equipment_id"]
            counts["decision_count"] += 1
            counts["known_truth_count"] += int(truth is not None)
            correct = None
            if disposition in ("accepted_automatic", "accepted_review"):
                if not equipment:
                    raise InputError("An accepted decision requires an equipment identifier")
                counts["accepted"] += 1
                if truth is None:
                    counts["accepted_without_known_truth"] += 1
                else:
                    correct = equipment == truth
                    counts["accepted_correct" if correct else "accepted_incorrect"] += 1
            elif disposition in ("review_required", "unresolved", "rejected"):
                if equipment is not None:
                    raise InputError("An unaccepted decision cannot carry an accepted identifier")
                counts[disposition] += 1
            else:
                raise InputError("Unrecognized comparison disposition")
            rows.append({"case_id": case["case_id"], "subject_record_id": decision["subject_record_id"],
                         "disposition": disposition, "accepted_equipment_id": equipment,
                         "physical_equipment_id": truth, "accepted_mapping_correct": correct})
    counts["acceptance_coverage"] = {"numerator": counts["accepted"], "denominator": counts["decision_count"]}
    counts["incorrect_among_scorable_accepts"] = {"numerator": counts["accepted_incorrect"],
                                                "denominator": counts["accepted_correct"] + counts["accepted_incorrect"]}
    return {"counts": counts, "decisions": rows}


def compare(automatic, baseline, reviewed, expected):
    if automatic["input_hash"] != baseline["input_hash"]:
        raise InputError("Automatic methods must receive identical inputs")
    for result in (automatic, baseline):
        if any(d["disposition"] == "accepted_review" for c in result["cases"] for d in c["decisions"]):
            raise InputError("Scripted-review outcomes cannot enter automatic comparison")
    return {"comparison_version": "ogard-comparison-1", "expectations_hash": digest(expected),
            "automatic_input_hash": automatic["input_hash"],
            "baseline_automatic": score(baseline, expected), "ogard_automatic": score(automatic, expected),
            "ogard_with_scripted_review": score(reviewed, expected),
            "scope": "Five selected synthetic cases; population accuracy and operational benefit require separate evaluation.",
            "unknown_truth_policy": "Unaccepted records are not counted as correct matches. Accepted records with no truth label are reported separately.",
            "review_policy": "Automatic comparison excludes all scripted review events from both methods."}


def render_markdown(comparison):
    lines = ["# OGARD synthetic comparison results", "", comparison["scope"], "",
             "The baseline accepts an explicit equipment identifier directly. If it is missing, it uses a unique installation at the record's receipt time. Ambiguous or missing installations remain unresolved. OGARD corroborates explicit identity at event time and routes missing identifiers or conflicts to review.", "",
             "| Measure | Baseline automatic | OGARD automatic | OGARD after scripted review |",
             "| --- | ---: | ---: | ---: |"]
    methods = [comparison[k]["counts"] for k in ("baseline_automatic", "ogard_automatic", "ogard_with_scripted_review")]
    for label, key in [("Total decisions", "decision_count"), ("Decisions with known synthetic physical truth", "known_truth_count"),
                       ("Accepted links", "accepted"), ("Correct accepted links", "accepted_correct"),
                       ("Incorrect accepted links", "accepted_incorrect"), ("Accepted without known truth", "accepted_without_known_truth"),
                       ("Review required", "review_required"), ("Unresolved", "unresolved"), ("Rejected", "rejected")]:
        lines.append("| " + label + " | " + " | ".join(str(m[key]) for m in methods) + " |")
    for label, key in [("Accepted / all decisions", "acceptance_coverage"), ("Incorrect / scorable accepted links", "incorrect_among_scorable_accepts")]:
        lines.append("| " + label + " | " + " | ".join(f'{m[key]["numerator"]}/{m[key]["denominator"]}' for m in methods) + " |")
    lines.extend(["", comparison["review_policy"], "", comparison["unknown_truth_policy"], "",
                  "## What changes in these cases", "",
                  "OGARD avoids automatically accepting the stale telemetry association and asks for review of the work order without a physical identifier. The baseline accepts that work-order association correctly in this example, so the extra review is a real workload trade-off. Both methods retain the wrong automatic association when sources share the same upstream error. Both handle the late record with an explicit identifier correctly. A separate regression test checks a late record without that identifier; it is not added to these six reported decisions.", "",
                  "The scripted review accepts one work-order association and defers one competing-installation case. It supplies no measured human performance. The competing-installation case has no single physical-truth label and is not scored as a correct equipment match.", "",
                  "## Decision detail", "",
                  "| Case and record | Baseline automatic | OGARD automatic | OGARD after scripted review |",
                  "| --- | --- | --- | --- |"])
    indexed = [{(r["case_id"], r["subject_record_id"]): r for r in comparison[k]["decisions"]}
               for k in ("baseline_automatic", "ogard_automatic", "ogard_with_scripted_review")]
    for key in indexed[0]:
        cells = []
        for method in indexed:
            row = method[key]
            cell = row["disposition"].replace("_", " ")
            if row["accepted_equipment_id"]:
                correctness = "correct" if row["accepted_mapping_correct"] is True else "incorrect" if row["accepted_mapping_correct"] is False else "truth unknown"
                cell += ": " + row["accepted_equipment_id"] + " (" + correctness + ")"
            cells.append(cell)
        lines.append("| " + " / ".join(key) + " | " + " | ".join(cells) + " |")
    lines.extend(["", "## Interpretation", "",
                  "These selected synthetic examples illustrate behavior and a known failure. Utility-data accuracy, comparisons with other products, outage reduction, adoption and production readiness require representative data and their own evaluation designs.", ""])
    return "\n".join(lines)
