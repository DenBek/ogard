# Input contract

This contract describes the executable reference implementation in release 0.2.1. All supplied data are synthetic. The processing code uses explicit approved identifiers and installation intervals.

## Source groups and structure

Three source groups provide equipment and installation history, maintenance work orders, and telemetry-to-equipment associations. Scripted review records exercise a separate decision workflow. A telemetry record represents an association at an event time, not a sensor-value stream.

The canonical JSON document has `schema_version: ogard-demo-source-1`, a `data_classification` description, a `profile` describing the fixture conventions, and a non-empty `cases` array. Each case has a unique non-empty `case_id`, `title`, `description`, and non-empty `records` array. Case names never select processing rules.

| Record | Required fields beyond the common fields | Optional fields |
| --- | --- | --- |
| Every record | `record_id`, `source_system`, `type`, `received_at` | Additional source metadata is retained |
| `installation` | `location_id`, `equipment_id`, `valid_from` | `valid_to`, null or omitted for an open interval |
| `work_order` | `location_id`, `event_at` | `equipment_id`, null or omitted when missing |
| `telemetry_link` | `location_id`, `event_at` | `equipment_id`, null or omitted when missing |
| `review` | `subject_record_id`, `actor`, `role`, `action`, `reason`, `evidence_ids` | `equipment_id`, required for acceptance |

Identifiers and source names are non-empty strings; record identifiers are unique within a case. `evidence_ids` is a non-empty array of distinct record identifiers. Duplicate JSON object keys, invalid record types, missing required values and malformed timestamps fail explicitly. The runner stops rather than dropping invalid records silently. This package uses a validated JSON contract; it does not claim general JSON Schema conformance.

## Time and arrival order

All processing timestamps are ISO 8601 values with explicit timezone offsets. Comparisons use UTC. Day-only values and timezone-naive timestamps are rejected. An installation includes `valid_from` and excludes `valid_to`: `[start, end)`. A finite end must be later than the start.

Records are processed by `received_at`; equal receipt timestamps retain their order in the input array. Only evidence already received can support a decision. A later installation record can revise an earlier decision while retaining its history. Equipment candidates are selected at the source record's `event_at`, including for a work order received after replacement.

The older worked-example JSON uses calendar-day intervals. Its projection into this executable package explicitly interprets the last installation day as ending at the next midnight in UTC. This conversion is recorded in provenance and is not an implicit engine rule for new data.

## Decisions and review

One time-valid installation corroborating the explicit equipment identifier permits automatic acceptance. A missing physical identifier requires review even with a single candidate. Conflicting candidates or contradictory explicit identities require review. No time-valid installation yields an unresolved association.

Each decision retains the subject record, event time, candidates, accepted equipment or null, disposition, reason, supporting evidence identifiers, contradictions and rule version. Input records, a ledger, and a hash-linked audit sequence accompany the decisions.

Reviews target one record. Work-order review uses role `asset_reviewer`; telemetry review uses `telemetry_owner`. `accept` requires a supported, unconflicted candidate and citations to all supporting evidence already available. `defer` leaves an unresolved association; `reject` records rejection. A work-order acceptance cannot clear a telemetry conflict. Changed relevant evidence invalidates the prior review snapshot and reopens the decision.

Actors and roles in these fixtures are declared synthetic values. The implementation validates the workflow profile; it does not authenticate real users. Audit hash links detect inconsistency against retained records, not a privileged rewrite of every record and hash.

## Alternate source layout

`demonstrator/data/layout-b.json` contains the same five scenarios using different field names, record-type codes, equipment codes and location codes. `layout-b-mapping.json` explicitly maps those approved values into the canonical contract. For example, `RecordKey` becomes `record_id`, `OccurredUTC` becomes `event_at`, and `WORK` becomes `work_order`.

The adapter rejects unmapped fields and identifiers and field mappings that would overwrite a canonical value. It preserves record identifiers, evidence references, times and ordering. The normalized document and complete processing output must equal the canonical version. The same matching engine is used for both layouts. This establishes limited synthetic portability, not a live utility integration.
