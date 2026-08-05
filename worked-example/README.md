# Synthetic Transformer Worked Example

## Purpose

This small, non-executable example demonstrates how OGARD relates source evidence, canonical context, mapping decisions, authorized review, contradiction handling, derived status, and audit records.

It does not determine the physical condition of a transformer and does not report production or benchmark performance.

## Scenario

A corrective maintenance work order identifies functional location `FL-NE-SUB114-TX02` but contains no equipment serial. Time-valid installation history makes replacement unit `TR-26-778204` the leading equipment candidate. The illustrative score remains below the automatic-acceptance threshold, so the case is routed to review.

The synthetic authorized reviewer accepts the replacement unit using the work-order date and installation history. Historian tag `NE114.TX2.OILTMP` still points to former unit `TR-88-104553`. OGARD preserves this as `TELEMETRY_EQUIPMENT_CONFLICT`. Any dependent status remains `Unknown` until authorized resolution.

## Files

- `source-records.json`: synthetic work order, register, installation, and historian evidence
- `canonical-context.json`: functional location, equipment units, installations, telemetry, and canonical asset context
- `mapping-decision.json`: deterministic location decision and review-routed equipment candidate
- `review-action.json`: authorized synthetic review outcome
- `contradiction.json`: stale telemetry-to-equipment relationship
- `derived-status.json`: controlled `Unknown` outcome and non-claim
- `illustrative-rules.json`: non-production illustrative rules
- `audit-log.json`: traceable record sequence

Reference artifacts are stored separately in `../reference/`:

- `contradiction-taxonomy-v0.1.json`
- `indicative-cim-crosswalk-v0.1.json`
- `scenario-catalogue-v0.1.json`

## Claim boundary

All records are synthetic and identify their OGARD model-profile and schema versions. The example is for inspection and discussion only. It is not an operator implementation, reference software, or evidence of operational outcomes.
