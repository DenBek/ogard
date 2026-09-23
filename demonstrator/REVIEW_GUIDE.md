# Reproduce and inspect OGARD

This guide covers executable release 0.2.0. It provides a complete procedure; it contains no prewritten endorsement or unsigned attestation. A fresh technical run can establish reproducibility, while a domain assessment separately addresses the workflow's realism and usefulness.

## Reproduce a fixed source revision

Obtain the repository snapshot for the commit being assessed. From its root, record the commit and run:

```sh
git rev-parse HEAD
python --version
python run_validation.py --output ../ogard-review --verify-snapshot
```

A downloaded ZIP does not contain Git metadata. In that case, retain the exact commit URL from which it was downloaded and the source inventory fingerprint in the run manifest.

Python 3.12 or later is sufficient. For an isolated environment, create a virtual environment with `python -m venv ../ogard-review-env` and use its Python interpreter. No packages need installation. The root command runs all tests and verifies the results, website links and checksum inventory. Exit code zero and `all_checks_passed: true` in `release_validation.json` mean those automated gates completed successfully.

## Inspect the evidence

Open `../ogard-review/walkthrough.html`. Compare `comparison.md` with `comparison.json`. Check that C01 retains a telemetry conflict after the scripted work-order acceptance; C02 maps the late record to the former unit; C03 retains competing histories; C04 accepts a supported identifier; and C05 records the wrong acceptance in the separate truth evaluation.

Inspect `adaptation.json` and `layout_b_normalized.json` to confirm the alternate layout preserves the full canonical input and decisions. Inspect `automatic_decisions.json` alongside `baseline_decisions.json`; neither automatic run receives scripted-review events. Inspect the revision sequence and evidence references in `decisions.json`.

## Record an external assessment

Retain the generated output directory and the exact source revision. In the reviewer's own record, identify the commands actually run, interpreter and operating system, matching or differing results, inspected files, modifications made, and the technical conclusions the reviewer can personally support. Describe technical reproduction separately from electricity-network experience or an assessment of operational usefulness.

The generated `run_manifest.json` and `release_validation.json` already contain completed execution facts and fingerprints. They do not name or authenticate the person operating the computer. Any signed assessment must come from the reviewer. Running the package alone does not establish operator adoption or measured operational outcomes.

## Scope of an assessment

The meaningful questions are whether identities and time intervals are applied consistently, whether ambiguity and contradictions remain visible, whether review actions respect the declared profile, whether evaluation labels stay out of processing, and whether the stated limitations accurately describe the results. The shared-source-error case is an expected failure of physical-identity inference, and must still count as an incorrect association.
