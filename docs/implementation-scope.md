# Implemented scope

Release 0.2.0 packages the executable transformer reference implementation and its measured synthetic results. The four version 0.1 papers remain the original methodology and design documents. Their broader design is not represented as completed software.

| Capability | Release 0.2.0 behavior |
| --- | --- |
| Identity and history | Separate location and equipment identifiers; installation intervals resolve event-time candidates |
| Evidence | Preserve inputs, source identifiers, receipt order and references supporting decisions |
| Reconciliation | Deterministic explicit-identifier corroboration; missing identity and material conflicts require review |
| Contradictions | Record competing installations and explicit-equipment or telemetry conflicts |
| Review | Accept, defer or reject under a synthetic role profile; changes in relevant evidence reopen decisions |
| Audit | Retain revisions and validate hash links, evidence availability and record accounting |
| Input adaptation | Two documented synthetic source layouts use the same processing logic |
| Evaluation | Separate workflow expectations and physical-truth labels; evaluate a simple baseline on identical automatic inputs |
| Reproduction | Python standard library, one-command validation, saved results and source/output fingerprints |

The five scenarios are C01 replacement with stale telemetry, C02 a late historical work order, C03 competing installation histories, C04 consistent evidence, and C05 a shared-source identity error. C01 has two relationship decisions, giving six in total. Targeted regression variations test boundaries without inflating that six-decision evaluation set.

## Defined limitations

The shared-source error remains an incorrect automatic acceptance. No contradictory physical evidence is available to either processing method. The evaluator detects the error using separately held synthetic truth; those labels are never processing inputs.

The implementation does not provide similarity scoring, machine learning, derived equipment-condition statuses, sensor analytics, cloud integrations, live reviewer authentication, a production data platform or operational control. The original reference example's score and `Unknown` condition-status fields remain illustrative design records. The executable decisions instead use deterministic rules and association dispositions.

These selected examples establish runnable behavior, transparent comparison and repeatability. They do not establish utility-data accuracy, operator adoption, production readiness, outage reduction, formal CIM compliance or independent expert endorsement.
