# Development provenance

Underlying OGARD methodology, architecture and original synthetic transformer example: Deniz Bektas. The original public repository revision used for this integration was `09d9dbfd98ebc1dbcacb3f0825e9e91e4aa09e62`.

The separately retained `OGARD_Initial_Demonstrator_v0_1.zip` contained working package 0.1.0-demo.1. Its original engine, cases, evaluator, tests and reporting structure form the basis of release 0.2.0. `provenance/original-baseline.json` records the archive fingerprint, a successful rerun of its 15 tests, and exact reproduction of its three saved deterministic outputs before integration.

Authored by Deniz Bektas. This development record documents implementation and automated validation. Separately documented expert assessments have their own scope and reviewed version. Synthetic review actors are scripted records for the demonstration.

## Original example projection

The canonical executable input preserves the original distinction between functional location, installed equipment and telemetry identity. The original example's old installation was valid through 14 April 2026. Its executable interval ends at 00:00 UTC on 15 April, exclusive; the replacement interval begins at that instant. Source day values were explicitly projected into this test convention. The engine itself requires timezone-aware timestamps.

The original reference example includes an illustrative similarity score and a derived `Unknown` status. They remain in the root `worked-example/` as design artifacts. The executable package implements deterministic identity and interval rules, association dispositions, contradictions and review history; it does not implement similarity scores or equipment-condition derivation.

## Release 0.2.0 additions

This release integrates the existing software into the public source tree, tightens malformed-input checks, adds a second synthetic source layout and explicit mapping, implements an explicit-ID-or-current-location baseline, separates automatic comparisons from scripted review, and produces reproducible comparison records. The runner verifies inputs and outputs and records content fingerprints. Documentation, licensing and website navigation identify the executable scope separately from the original design papers.

The five original scenarios and separate truth labels are retained. The shared-source identity error remains an incorrect automatic acceptance. Evaluation labels are read after processing, so the shared-source error remains observable in the results. The implementation uses original code, synthetic records and public reference material.

## Release 0.2.1 corrections

The September 16 whitepaper is the canonical technical manuscript, issued as public edition v0.1.1 on 24 September 2026. Companion papers receive editorial publication-status corrections with technical content unchanged. Python support starts at 3.10; the automated validation record describes its own scope separately from expert assessments. Processing rules, synthetic inputs, truth labels and measured decision counts are unchanged from 0.2.0.
