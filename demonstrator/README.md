# OGARD executable reference implementation

Release **0.2.1** connects transformer maintenance and telemetry records to equipment history using explicit identifiers, installation intervals, preserved conflicts and documented review. Five synthetic scenarios produce six equipment-association decisions. Two source layouts exercise the same engine.

## Run the complete release

Use Python 3.10 or later. No external packages, cloud accounts or credentials are required. From the repository root:

```sh
python run_validation.py --output ../ogard-rerun --verify-snapshot
```

Use `python3` if that is your interpreter command. This verifies tests, both input layouts, workflow evaluation, the baseline comparison, all supplied deterministic outputs, local website links and release checksums. Open `../ogard-rerun/walkthrough.html` to inspect the results. A nonzero exit status indicates failure.

To regenerate the software outputs during development, from this directory:

```sh
python run_demo.py
```

This writes `results/`. Reproducible release verification uses the root command above, which preserves the supplied results.

## Contents

| Path | Purpose |
| --- | --- |
| `ogard_demo/engine.py` | Evidence-only deterministic processing and review history |
| `data/cases.json` | Five canonical synthetic scenarios |
| `data/layout-b.json` | Equivalent records with different source columns and codes |
| `data/layout-b-mapping.json` | Explicit approved mapping into the canonical contract |
| `evaluation/expectations.json` | Separate workflow expectations and physical-truth labels |
| `ogard_demo/baseline.py` | Simple explicit-ID-or-current-location comparator |
| `ogard_demo/comparison.py` | Counts, denominators and per-record comparison |
| `tests/` | Temporal, review, input, adaptation, evaluation and integrity checks |
| `results/` | Complete supplied execution outputs and fingerprints |
| `REVIEW_GUIDE.md` | Exact reproduction and inspection procedure |
| `PROVENANCE.md` | Development history and relationship to the original example |

## Processing individual inputs

From this directory:

```sh
python -m ogard_demo process --input data/cases.json --output ../ogard-decisions.json
python -m ogard_demo normalize --input data/layout-b.json --mapping data/layout-b-mapping.json --output ../ogard-normalized.json
python -m ogard_demo evaluate --decisions ../ogard-decisions.json --expectations evaluation/expectations.json --output ../ogard-evaluation.json
```

Evaluation labels never enter processing. The release runner finalizes both automatic methods and the scripted-review demonstration before reading labels. The command-line baseline ignores review events.

## Results and limits

The baseline automatically accepts five of six links: three correct and two incorrect. OGARD automatically accepts three: two correct and one incorrect, with three referrals to review. With scripted review, OGARD retains four accepted links, one telemetry referral and one unresolved association. One accepted link is wrong in the shared-source-error case.

These are selected synthetic examples, not a representative utility benchmark. Scripted review is distinct from a real reviewer running the package. See the [input contract](../docs/input-contract.md), [evaluation method](../docs/evaluation-method.md), [scope](../docs/implementation-scope.md) and generated [comparison](results/comparison.md).

The engine does not implement similarity scoring, derived asset condition, production authentication or operational control. Original code is Apache-2.0; documentation and structured synthetic data are CC-BY-4.0. See the root [license](../LICENSE.md).
