# OGARD

**Open Grid Asset Reliability Data Framework**

OGARD provides a reusable methodology and executable reference implementation for reconciling electricity-network equipment records across maintenance, installation history and telemetry associations. It preserves evidence, time validity, conflicting accounts and review decisions.

**Current release:** 0.2.0 - executable transformer reference implementation
**Author:** Deniz Bektas
**Website:** https://denbek.github.io/ogard/
**Repository:** https://github.com/DenBek/ogard

## Run and verify

Python 3.12 or later is sufficient. No third-party packages, credentials or cloud services are required. From the repository root:

```sh
python run_validation.py --output ../ogard-rerun --verify-snapshot
```

Use `python3` where appropriate. The command verifies the regression suite, both synthetic source layouts, workflow behavior, baseline comparison, supplied deterministic outputs, local website links and release checksums. Open `../ogard-rerun/walkthrough.html` for the generated explanation. The [review guide](demonstrator/REVIEW_GUIDE.md) explains how to record a reproduction of a fixed source revision.

## What is implemented

- Explicit equipment identity corroborated by event-time installation history.
- Preserved source evidence, conflicts, decision revisions and review records.
- Review for missing identifiers and conflicting candidates; unresolved outcomes where evidence is insufficient.
- Two documented input layouts mapped into the same processing engine.
- A simple baseline, separate physical-truth evaluation and reproducible result reports.

Five selected synthetic cases produce six decisions. The baseline automatically accepts five links, including two incorrect ones. OGARD automatically accepts three, including one incorrect one, and refers three to review. Scripted review is reported separately. [Inspect the complete comparison](demonstrator/results/comparison.md).

These counts illustrate specified behavior and a retained shared-source-error limitation. They do not estimate utility-data accuracy, operational benefit or adoption. See the [implemented scope](docs/implementation-scope.md).

## Repository contents

| Path | Contents |
| --- | --- |
| `demonstrator/` | Executable code, inputs, mappings, labels, tests, results and reviewer instructions |
| `docs/` | Input contract, scope, evaluation method and release validation record |
| `papers/` | Four original version 0.1 methodology and design PDFs |
| `diagrams/` | System context, logical architecture and entity relationships |
| `worked-example/` | Original non-executable transformer design example |
| `reference/` | Contradiction taxonomy, indicative CIM crosswalk and broader scenario catalogue |
| `assets/` and root HTML | Static GitHub Pages website, including the implementation page |
| `release-manifest.json` and `SHA256SUMS.txt` | Versioned inventory and file integrity checks |

The original papers cover a broader program, including similarity methods and derived statuses. The current software scope is stated separately; release 0.2.0 does not claim completion of that broader design or the full benchmark plan.

## Document set

1. Technical Whitepaper.
2. Implementation Guide.
3. Architecture and Data Model Specification.
4. Synthetic Benchmark Methodology and Validation Plan.

All four PDFs retain their original version 0.1 labels. Current executable results are in `demonstrator/results/`, not retroactively attributed to those original papers.

## Citation and reuse

Bektas, D. (2026). *OGARD: Open Grid Asset Reliability Data Framework*. Executable Reference Release 0.2.0. https://github.com/DenBek/ogard

Original executable and website code is Apache-2.0. Documentation, diagrams and structured synthetic data are CC-BY-4.0. See [LICENSE.md](LICENSE.md) and [development provenance](demonstrator/PROVENANCE.md).

Use [GitHub Issues](https://github.com/DenBek/ogard/issues) for reproducible technical feedback. Do not post confidential employer, client or utility information.
