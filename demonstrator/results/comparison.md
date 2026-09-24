# OGARD synthetic comparison results

Five selected synthetic cases; population accuracy and operational benefit require separate evaluation.

The baseline accepts an explicit equipment identifier directly. If it is missing, it uses a unique installation at the record's receipt time. Ambiguous or missing installations remain unresolved. OGARD corroborates explicit identity at event time and routes missing identifiers or conflicts to review.

| Measure | Baseline automatic | OGARD automatic | OGARD after scripted review |
| --- | ---: | ---: | ---: |
| Total decisions | 6 | 6 | 6 |
| Decisions with known synthetic physical truth | 5 | 5 | 5 |
| Accepted links | 5 | 3 | 4 |
| Correct accepted links | 3 | 2 | 3 |
| Incorrect accepted links | 2 | 1 | 1 |
| Accepted without known truth | 0 | 0 | 0 |
| Review required | 0 | 3 | 1 |
| Unresolved | 1 | 0 | 1 |
| Rejected | 0 | 0 | 0 |
| Accepted / all decisions | 5/6 | 3/6 | 4/6 |
| Incorrect / scorable accepted links | 2/5 | 1/3 | 1/4 |

Automatic comparison excludes all scripted review events from both methods.

Unaccepted records are not counted as correct matches. Accepted records with no truth label are reported separately.

## What changes in these cases

OGARD avoids automatically accepting the stale telemetry association and asks for review of the work order without a physical identifier. The baseline accepts that work-order association correctly in this example, so the extra review is a real workload trade-off. Both methods retain the wrong automatic association when sources share the same upstream error. Both handle the late record with an explicit identifier correctly. A separate regression test checks a late record without that identifier; it is not added to these six reported decisions.

The scripted review accepts one work-order association and defers one competing-installation case. It supplies no measured human performance. The competing-installation case has no single physical-truth label and is not scored as a correct equipment match.

## Decision detail

| Case and record | Baseline automatic | OGARD automatic | OGARD after scripted review |
| --- | --- | --- | --- |
| C01 / EV-WO-2026-0512 | accepted automatic: EQ-TR-NEW-01 (correct) | review required | accepted review: EQ-TR-NEW-01 (correct) |
| C01 / EV-HIST-TX2-OIL | accepted automatic: EQ-TR-OLD-01 (incorrect) | review required | review required |
| C02 / WO-LATE | accepted automatic: EQ-TR-OLD-01 (correct) | accepted automatic: EQ-TR-OLD-01 (correct) | accepted automatic: EQ-TR-OLD-01 (correct) |
| C03 / WO-AMBIGUOUS | unresolved | review required | unresolved |
| C04 / WO-CLEAN | accepted automatic: EQ-TR-NEW-01 (correct) | accepted automatic: EQ-TR-NEW-01 (correct) | accepted automatic: EQ-TR-NEW-01 (correct) |
| C05 / WO-SHARED-ERROR | accepted automatic: EQ-SHARED-WRONG (incorrect) | accepted automatic: EQ-SHARED-WRONG (incorrect) | accepted automatic: EQ-SHARED-WRONG (incorrect) |

## Interpretation

These selected synthetic examples illustrate behavior and a known failure. Utility-data accuracy, comparisons with other products, outage reduction, adoption and production readiness require representative data and their own evaluation designs.
