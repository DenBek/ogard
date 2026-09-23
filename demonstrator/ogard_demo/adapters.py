"""Explicit source-layout projection; no matching or truth labels here."""

import copy

from .engine import InputError, validate_document


def normalize_layout_b(source, mapping):
    if not isinstance(source, dict) or source.get("schema_version") != "ogard-source-layout-b-1":
        raise InputError("Expected schema_version ogard-source-layout-b-1")
    if not isinstance(mapping, dict) or mapping.get("mapping_version") != "ogard-layout-b-map-1":
        raise InputError("Expected mapping_version ogard-layout-b-map-1")
    for key in ("fields", "record_types", "equipment_ids", "location_ids"):
        values = mapping.get(key)
        if not isinstance(values, dict) or not values:
            raise InputError("Mapping requires " + key)
        if any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
               for k, v in values.items()):
            raise InputError("Mapping entries must be non-empty strings")
    if len(set(mapping["fields"].values())) != len(mapping["fields"]):
        raise InputError("Multiple source fields cannot overwrite one canonical field")
    if not isinstance(source.get("scenarios"), list) or not source["scenarios"]:
        raise InputError("Layout B requires a non-empty scenarios array")
    result = {"schema_version": "ogard-demo-source-1",
              "data_classification": source.get("data_classification"),
              "profile": copy.deepcopy(source.get("profile", {})), "cases": []}
    for scenario in source["scenarios"]:
        if not isinstance(scenario, dict) or set(scenario) != {"scenario", "name", "narrative", "rows"}:
            raise InputError("Layout B scenario requires scenario, name, narrative and rows")
        if not isinstance(scenario["rows"], list):
            raise InputError("Layout B rows must be an array")
        case = {"case_id": scenario["scenario"], "title": scenario["name"],
                "description": scenario["narrative"], "records": []}
        for row in scenario["rows"]:
            if not isinstance(row, dict) or set(row) - set(mapping["fields"]):
                raise InputError("Unmapped or invalid source row")
            record = {mapping["fields"][key]: copy.deepcopy(value) for key, value in row.items()}
            for field, dictionary in (("type", "record_types"), ("equipment_id", "equipment_ids"),
                                      ("location_id", "location_ids")):
                value = record.get(field)
                if value is not None:
                    if not isinstance(value, str) or value not in mapping[dictionary]:
                        raise InputError("Unmapped " + field + ": " + str(value))
                    record[field] = mapping[dictionary][value]
            case["records"].append(record)
        result["cases"].append(case)
    validate_document(result)
    return result
