# OGARD

**Open Grid Asset Reliability Data Framework**

OGARD is an independently authored reference methodology for reconciling fragmented electricity-network asset evidence into auditable, operator-governed information products.

**Website:** https://denbek.github.io/ogard/  
**Author:** Deniz Bektas  
**Repository:** https://github.com/DenBek/ogard  
**Current status:** Public Reference Release v0.1

## What OGARD addresses

Grid assets are often represented differently across maintenance systems, asset registers, telemetry historians, work orders, inspections, fault records, and technical documents. OGARD provides a controlled method to:

- preserve source evidence and provenance
- separate functional location, physical equipment identity, and telemetry identity
- maintain time-valid relationships
- apply versioned deterministic rules and reproducible similarity methods
- route ambiguous or consequential cases to authorized review
- preserve material contradictions rather than silently overwriting them
- produce operator-governed outputs with explicit audit records and limitations

## Repository contents

- `papers/`: three aligned OGARD technical papers
- `diagrams/`: original system-context, logical-architecture, and entity-relationship diagrams
- `worked-example/`: synthetic transformer records covering evidence, mapping, review, contradiction, status, and audit
- `reference/`: contradiction taxonomy, indicative CIM crosswalk, and benchmark scenario catalogue
- `assets/` and root HTML files: static GitHub Pages website
- `release-manifest.json`: machine-readable package inventory 

## Document set

1. **Technical Whitepaper**: problem definition, contribution, framework, governance, and limitations.
2. **Implementation Guide**: readiness, roles, implementation sequence, review controls, testing, and production boundaries.
3. **Architecture and Data Model Specification**: minimum architecture, entities, conformance controls, contradiction taxonomy, and indicative CIM guidance.

## Synthetic worked example

The example follows one maintenance work order after a transformer replacement. The equipment mapping is reviewed and accepted using time-valid installation evidence. A historian tag remains associated with the former unit, so OGARD records `TELEMETRY_EQUIPMENT_CONFLICT` and keeps the dependent status `Unknown` until authorized resolution.

Start with [`worked-example/README.md`](worked-example/README.md) or view the [website walkthrough](https://denbek.github.io/ogard/architecture.html#worked-example).


## Citation

Bektas, D. (2026). *OGARD: Open Grid Asset Reliability Data Framework*. Public Reference Release v0.1. https://github.com/DenBek/ogard

## Licensing

Documentation, diagrams, and structured synthetic examples are provided under CC BY 4.0. Original website code is provided under Apache License 2.0. See [`LICENSE.md`](LICENSE.md).

## Technical feedback

Use [GitHub Issues](https://github.com/DenBek/ogard/issues) for corrections, implementation questions, taxonomy proposals, or reproducibility feedback. Do not post confidential, employer-controlled, client, or utility operational information.
