# Release validation record

Release 0.2.0 integrates the original transformer demonstrator and provides an executable source package, two input layouts, a baseline comparison and complete reproduction instructions.

## Completed software checks

The original package was first run without modification. Its 15 tests passed, and its decision JSON, evaluation JSON and generated walkthrough matched the retained originals byte for byte. The original archive fingerprint and reproduction result are recorded in `demonstrator/provenance/original-baseline.json`.

The integrated suite passes 33 regression tests. It covers event-time installation boundaries, timezone equivalence, late records, competing histories, review roles and supporting evidence, reopening review after changed evidence, audit modification, malformed inputs, duplicate JSON keys, alternate-layout mapping, truth isolation, complete evaluation inventories and fair automatic comparisons.

The second source layout normalizes to the same canonical input and produces identical decisions. The supplied results retain all five scenarios and six decisions. The shared-source error remains one incorrect automatic acceptance. Automatic comparisons exclude review events from both methods, and the scripted-review demonstration is reported separately.

## Reproducibility and integrity

The root validation command reproduces ten deterministic outputs and compares them with the supplied snapshots. Source fingerprints verify that the saved run used the current implementation and documentation. The checksum inventory covers the packaged source, website, records and original PDFs. Local website references and HTML fragment destinations are checked automatically.

Use this exact command from the repository root:

```sh
python run_validation.py --output ../ogard-rerun --verify-snapshot
```

A successful run writes `release_validation.json` with the completed gate results and `run_manifest.json` with runtime information and source/output fingerprints. The saved test transcript is in `demonstrator/results/test_results.txt`. Runtime timestamps, platform strings and test durations are intentionally not required to match across machines.

The GitHub validation workflow runs this same command against the event's exact source revision, using read-only repository permissions. Its result is recorded by GitHub separately from the source release.

## Interpretation

Passing software and reproducibility checks establishes the behavior and repeatability of this defined reference implementation. It does not erase the known synthetic identity error or establish external expert review, production performance or operator adoption. Real reviewer assessments must identify the source revision and the work personally performed by that reviewer.
