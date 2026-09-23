"""Simple explicit-ID or current-location lookup, without OGARD corroboration."""

import copy

from .engine import digest, instant, validate_document

BASELINE_VERSION = "explicit-id-or-current-location-1"


def without_reviews(document):
    result = copy.deepcopy(document)
    for case in result["cases"]:
        case["records"] = [r for r in case["records"] if r["type"] != "review"]
    return result


def process_baseline(document):
    validate_document(document)
    cases = []
    for case in document["cases"]:
        evidence, queries, current = {}, {}, {}
        chronology = sorted(enumerate(case["records"]), key=lambda item: (instant(item[1]["received_at"]), item[0]))
        for _, record in chronology:
            if record["type"] == "review":
                continue
            evidence[record["record_id"]] = record
            if record["type"] in ("work_order", "telemetry_link"):
                queries[record["record_id"]] = record
            for sid, query in sorted(queries.items()):
                selected = query.get("equipment_id")
                refs = [sid]
                reason = "EXPLICIT_ID_LOOKUP"
                if selected is None:
                    at = instant(query["received_at"])
                    installs = [r for r in evidence.values() if r["type"] == "installation"
                                and r["location_id"] == query["location_id"]
                                and instant(r["valid_from"]) <= at
                                and (r.get("valid_to") is None or at < instant(r["valid_to"]))]
                    candidates = sorted({r["equipment_id"] for r in installs})
                    refs.extend(r["record_id"] for r in installs)
                    selected = candidates[0] if len(candidates) == 1 else None
                    reason = "UNIQUE_CURRENT_LOCATION_LOOKUP" if selected else "NO_UNIQUE_CURRENT_INSTALLATION"
                current[sid] = {"subject_record_id": sid, "record_type": query["type"],
                                "accepted_equipment_id": selected,
                                "disposition": "accepted_automatic" if selected else "unresolved",
                                "reason_code": reason, "evidence_ids": sorted(set(refs))}
        cases.append({"case_id": case["case_id"], "decisions": list(current.values())})
    return {"baseline_version": BASELINE_VERSION, "input_hash": digest(document), "cases": cases}
