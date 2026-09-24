# Evaluation method

Processing and evaluation answer different questions. Regression checks test specified behavior. Separate synthetic truth labels assess whether accepted equipment links are correct. A workflow can execute as specified and still accept the wrong physical identity.

## Frozen inputs and labels

The five source cases are in `demonstrator/data/cases.json`. Workflow expectations and physical-truth labels are in `demonstrator/evaluation/expectations.json`. The evaluator reads finalized processing outputs before comparing them with labels. Neither the engine, input adapter nor baseline reads evaluation labels. Labels are published for inspection and withheld from processing. They belong to the selected examples; a statistically independent holdout dataset is a separate evaluation requirement.

One decision, the competing-installation case, has no single physical-truth label. The other five do. Unaccepted decisions do not count as correct matches. An accepted decision without a known truth label is reported separately and is excluded from the correct/incorrect accepted-link denominator.

## Baseline

The explicit-ID-or-current-location baseline accepts an explicit equipment identifier without historical corroboration. If that identifier is absent, it uses a unique installation active at the record's receipt time. Multiple or missing candidates remain unresolved. It preserves ambiguity instead of arbitrarily choosing a candidate. It is a defined comparator for these cases. Comparisons with other utility processes or products require their own implementations and evaluation design.

Both automatic methods receive exactly the same source document with scripted review events removed. Both process sources in receipt order and use only the available evidence. The source fingerprint must match. The baseline revisits records as installation evidence arrives, just as the OGARD automatic run can. Its installation lookup uses the subject record's receipt time; OGARD uses event time and corroborates explicit identity.

A separate OGARD run includes the scripted review records. Its outcomes never enter the automatic comparison. There is no measured human-review accuracy or duration in these fixtures.

## Measures

Results include total decisions, known-truth decisions, accepted links, correct and incorrect accepted links, accepted links without known truth, review referrals, unresolved decisions and rejections. Acceptance coverage is accepted links divided by all decisions. Incorrect-acceptance fraction is incorrect links divided by scorable accepted links. Counts and denominators are retained; small-sample percentages are not presented as population accuracy.

`demonstrator/results/comparison.md` and `comparison.json` provide the generated aggregate and per-record results. The known shared-source error remains visible. The comparison describes both avoided wrong acceptance and additional review workload.

## Validation gates

The release command fails on failed tests, workflow/integrity discrepancies, mismatched decision inventories, unequal automatic inputs, second-layout differences, stale supplied snapshots, invalid local website links or mismatched release checksums. A deliberately disclosed physical-truth error does not pass as a correct match; it is counted as an incorrect acceptance. Its expected presence is a tested limitation of the algorithm, not an execution failure.

Runtime timestamps, platform strings and test durations can differ between machines. Decision files, labels-based evaluation, input adaptation, comparison tables and generated walkthroughs are deterministic and are compared byte for byte when verifying the supplied snapshot.
