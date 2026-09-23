"""Evidence-only processing. This module never reads evaluation expectations."""

import copy
import hashlib
import json
from datetime import datetime, timezone

RULE_VERSION = "ogard-explicit-temporal-2"


class InputError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def instant(value):
    if not isinstance(value, str):
        raise InputError("An explicit timezone-aware timestamp is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputError("Invalid timestamp: " + value) from exc
    if parsed.tzinfo is None:
        raise InputError("Timestamp has no timezone: " + value)
    return parsed.astimezone(timezone.utc)


def validate(case):
    if not isinstance(case, dict):
        raise InputError("Each case must be an object")
    for key in ("case_id", "title", "description"):
        if not isinstance(case.get(key), str) or not case[key].strip():
            raise InputError("Case requires a non-empty " + key)
    if not isinstance(case.get("records"), list) or not case["records"]:
        raise InputError("Case requires a non-empty records array")
    records = case["records"]
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise InputError("Each record must be an object")
        rid = record.get("record_id")
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            raise InputError("Missing or duplicate record identifier")
        seen.add(rid)
        if not isinstance(record.get("source_system"), str) or not record["source_system"].strip():
            raise InputError(rid + ": missing source system")
        for key in ("equipment_id", "location_id"):
            if key in record and record[key] is not None:
                if not isinstance(record[key], str) or not record[key].strip():
                    raise InputError(rid + ": " + key + " must be a non-empty string or null")
        instant(record.get("received_at"))
        kind = record.get("type")
        if kind == "installation":
            for key in ("location_id", "equipment_id", "valid_from"):
                if not record.get(key):
                    raise InputError(rid + ": missing " + key)
            start = instant(record["valid_from"])
            if record.get("valid_to") is not None and instant(record["valid_to"]) <= start:
                raise InputError(rid + ": empty or reversed installation interval")
        elif kind in ("work_order", "telemetry_link"):
            if not record.get("location_id"):
                raise InputError(rid + ": missing location identifier")
            instant(record.get("event_at"))
        elif kind == "review":
            for key in ("subject_record_id", "actor", "role", "action", "reason"):
                if not isinstance(record.get(key), str) or not record[key].strip():
                    raise InputError(rid + ": missing " + key)
            if record["action"] not in ("accept", "defer", "reject"):
                raise InputError(rid + ": unsupported review action")
            refs = record.get("evidence_ids")
            if (not isinstance(refs, list) or not refs
                    or any(not isinstance(ref, str) or not ref.strip() for ref in refs)
                    or len(refs) != len(set(refs))):
                raise InputError(rid + ": review must cite evidence")
        else:
            raise InputError(rid + ": unsupported record type")


def assess(query, evidence):
    event = instant(query["event_at"])
    installs = [r for r in evidence.values() if r["type"] == "installation"
                and r["location_id"] == query["location_id"]
                and instant(r["valid_from"]) <= event
                and (r.get("valid_to") is None or event < instant(r["valid_to"]))]
    installs.sort(key=lambda r: r["record_id"])
    candidates = sorted({r["equipment_id"] for r in installs})
    refs = sorted({query["record_id"], *(r["record_id"] for r in installs)})
    contradictions = []
    explicit = query.get("equipment_id")
    if len(candidates) > 1:
        contradictions.append({"code": "COMPETING_INSTALLATIONS", "evidence_ids": refs})
    if explicit and candidates and explicit not in candidates:
        code = "TELEMETRY_EQUIPMENT_CONFLICT" if query["type"] == "telemetry_link" else "EXPLICIT_EQUIPMENT_CONFLICT"
        contradictions.append({"code": code, "evidence_ids": refs})
    if not candidates:
        disposition, reason = "unresolved", "NO_INSTALLATION_EVIDENCE_AT_EVENT_TIME"
    elif contradictions:
        disposition, reason = "review_required", "CONFLICTING_ASSET_EVIDENCE"
    elif explicit == candidates[0]:
        disposition, reason = "accepted_automatic", "EXPLICIT_ID_CORROBORATED_BY_INSTALLATION"
    else:
        disposition, reason = "review_required", "PHYSICAL_IDENTIFIER_MISSING_REVIEW_REQUIRED"
    return {
        "subject_record_id": query["record_id"], "record_type": query["type"],
        "location_id": query["location_id"], "event_at": query["event_at"],
        "candidate_equipment_ids": candidates,
        "accepted_equipment_id": candidates[0] if disposition == "accepted_automatic" else None,
        "disposition": disposition, "reason_code": reason,
        "evidence_ids": refs, "contradictions": contradictions,
        "rule_version": RULE_VERSION,
    }


def apply_review(base, review):
    decision = copy.deepcopy(base)
    action = review["action"]
    decision["disposition"] = {"accept": "accepted_review", "defer": "unresolved", "reject": "rejected"}[action]
    decision["accepted_equipment_id"] = review.get("equipment_id") if action == "accept" else None
    decision["reason_code"] = "REVIEW_" + action.upper()
    decision["review_record_id"] = review["record_id"]
    decision["review_actor"] = review["actor"]
    decision["review_role"] = review["role"]
    decision["review_reason"] = review["reason"]
    decision["review_mode"] = "scripted_synthetic_event"
    decision["evidence_ids"] = sorted(set(base["evidence_ids"] + review["evidence_ids"]))
    return decision


def process_case(case):
    validate(case)
    evidence, queries, reviews, current, revisions = {}, {}, {}, {}, {}
    audit = []
    chronology = sorted(enumerate(case["records"]), key=lambda item: (instant(item[1]["received_at"]), item[0]))

    def log(event, trigger, **fields):
        entry = {"sequence": len(audit) + 1, "event": event,
                 "processed_at": trigger["received_at"], "trigger_record_id": trigger["record_id"],
                 "previous_hash": audit[-1]["entry_hash"] if audit else None, **fields}
        entry["entry_hash"] = digest(entry)
        audit.append(entry)
        return entry["sequence"]

    for _, source in chronology:
        record = copy.deepcopy(source)
        rid = record["record_id"]
        if record["type"] == "review":
            sid = record["subject_record_id"]
            if sid not in queries:
                raise InputError(rid + ": review subject not yet available")
            role = "telemetry_owner" if queries[sid]["type"] == "telemetry_link" else "asset_reviewer"
            if record["role"] != role:
                raise InputError(rid + ": role not authorized by this synthetic profile")
            if not set(record["evidence_ids"]).issubset(evidence):
                raise InputError(rid + ": review cites unavailable evidence")
            base = assess(queries[sid], evidence)
            if sid not in record["evidence_ids"]:
                raise InputError(rid + ": review must cite its source record")
            if record["action"] == "accept":
                if base["contradictions"] or len(base["candidate_equipment_ids"]) != 1:
                    raise InputError(rid + ": acceptance requires one supported, unconflicted candidate")
                if record.get("equipment_id") not in base["candidate_equipment_ids"]:
                    raise InputError(rid + ": accepted equipment is not supported")
                if not set(base["evidence_ids"]).issubset(record["evidence_ids"]):
                    raise InputError(rid + ": acceptance must cite supporting installation evidence")
            reviews[sid] = {"record": record, "base_signature": digest(base)}
        evidence[rid] = record
        log("source_received", record, source_hash=digest(record))
        if record["type"] in ("work_order", "telemetry_link"):
            queries[rid] = record
        for sid, query in sorted(queries.items()):
            decision = assess(query, evidence)
            review = reviews.get(sid)
            if review:
                if review["base_signature"] == digest(decision):
                    decision = apply_review(decision, review["record"])
                else:
                    decision["superseded_review_record_id"] = review["record"]["record_id"]
                    decision["accepted_equipment_id"] = None
                    decision["disposition"] = "review_required"
                    decision["reason_code"] = "EVIDENCE_CHANGED_SINCE_REVIEW"
            if decision != current.get(sid):
                revisions[sid] = log("decision_updated", record, subject_record_id=sid,
                                     supersedes_sequence=revisions.get(sid), decision=decision)
                current[sid] = decision
    counts = {}
    for decision in current.values():
        counts[decision["disposition"]] = counts.get(decision["disposition"], 0) + 1
    ledger = [{"record_id": r["record_id"], "kind": r["type"],
               "disposition": current[r["record_id"]]["disposition"] if r["record_id"] in current
               else "review_event_recorded" if r["type"] == "review" else "context_evidence_retained"}
              for r in case["records"]]
    return {"case_id": case["case_id"], "title": case["title"],
            "description": case["description"], "source_hash": digest(case),
            "source_records": copy.deepcopy(case["records"]),
            "decisions": list(current.values()), "decision_counts": counts,
            "input_ledger": ledger, "audit": audit,
            "limits": ["Explicit identifiers and installation intervals only; no similarity or derived-status calculation.",
                       "Reviewer names and roles are synthetic declarations, not authenticated human identities.",
                       "Hash links support consistency checks, not tamper-proof storage."]}


def process_document(document):
    validate_document(document)
    return {"schema_version": "ogard-demo-output-1", "rule_version": RULE_VERSION,
            "input_hash": digest(document), "cases": [process_case(c) for c in document["cases"]]}


def validate_document(document):
    if not isinstance(document, dict) or document.get("schema_version") != "ogard-demo-source-1":
        raise InputError("Expected schema_version ogard-demo-source-1")
    if not isinstance(document.get("cases"), list) or not document["cases"]:
        raise InputError("Document requires a non-empty cases array")
    for case in document["cases"]:
        validate(case)
    ids = [case["case_id"] for case in document["cases"]]
    if len(ids) != len(set(ids)):
        raise InputError("Duplicate case identifier")
