"""Validate both layouts, process, compare, and retain reproducible evidence."""

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ogard_demo import __version__
from ogard_demo.adapters import normalize_layout_b
from ogard_demo.baseline import process_baseline, without_reviews
from ogard_demo.comparison import compare, render_markdown
from ogard_demo.engine import digest, process_document
from ogard_demo.evaluate import evaluate_document
from ogard_demo.io import read_json, write_json
from ogard_demo.report import render_report

ROOT = Path(__file__).resolve().parent
STABLE_OUTPUTS = ("decisions.json", "automatic_decisions.json", "baseline_decisions.json", "evaluation.json",
                  "comparison.json", "comparison.md", "layout_b_normalized.json", "adaptation.json",
                  "walkthrough.html", "validation_summary.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out):
    out = Path(out).resolve()
    if out == ROOT or (ROOT in out.parents and out.relative_to(ROOT).parts[0] != "results"):
        raise ValueError("Use the results directory or an output directory outside the demonstrator")
    out.mkdir(parents=True, exist_ok=True)
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                           cwd=ROOT, capture_output=True, text=True)
    transcript = tests.stdout + tests.stderr
    (out / "test_results.txt").write_text(transcript, encoding="utf-8")
    count = re.search(r"Ran (\d+) tests?", transcript)
    if tests.returncode or not count or int(count.group(1)) == 0:
        raise RuntimeError("Test failure; inspect " + str(out / "test_results.txt"))
    inputs = read_json(ROOT / "data/cases.json")
    alternate = read_json(ROOT / "data/layout-b.json")
    mapping = read_json(ROOT / "data/layout-b-mapping.json")
    normalized = normalize_layout_b(alternate, mapping)
    decisions = process_document(inputs)
    alternative_decisions = process_document(normalized)
    if normalized != inputs or alternative_decisions != decisions:
        raise RuntimeError("Second-layout equivalence failed")
    automatic_inputs = without_reviews(inputs)
    automatic = process_document(automatic_inputs)
    baseline = process_baseline(automatic_inputs)
    # Labels are read only after all processing calls have finalized their outputs.
    expected = read_json(ROOT / "evaluation/expectations.json")
    evaluation = evaluate_document(decisions, expected)
    if not evaluation["all_workflow_checks_passed"]:
        raise RuntimeError("Workflow evaluation failed")
    comparison = compare(automatic, baseline, decisions, expected)
    adaptation = {"mapping_version": mapping["mapping_version"], "layout_b_input_hash": digest(alternate),
                  "mapping_hash": digest(mapping), "normalized_input_hash": digest(normalized),
                  "canonical_input_hash": digest(inputs), "inputs_identical": True, "decisions_identical": True,
                  "scope": "Two synthetic source layouts of the same five scenarios; no real operator integration is claimed."}
    summary = {"release_version": __version__, "tests_passed": int(count.group(1)), "tests_failed": 0,
               "case_count": len(inputs["cases"]), "decision_count": sum(len(c["decisions"]) for c in decisions["cases"]),
               "workflow_checks_passed": True, "source_layouts_verified": 2,
               "independent_external_review": "outside_scope_of_automated_run",
               "baseline_automatic": comparison["baseline_automatic"]["counts"],
               "ogard_automatic": comparison["ogard_automatic"]["counts"],
               "ogard_with_scripted_review": comparison["ogard_with_scripted_review"]["counts"]}
    for name, value in [("decisions.json", decisions), ("automatic_decisions.json", automatic),
                        ("baseline_decisions.json", baseline), ("evaluation.json", evaluation),
                        ("comparison.json", comparison), ("layout_b_normalized.json", normalized),
                        ("adaptation.json", adaptation), ("validation_summary.json", summary)]:
        write_json(out / name, value)
    (out / "comparison.md").write_text(render_markdown(comparison), encoding="utf-8")
    (out / "walkthrough.html").write_text(render_report(decisions, evaluation, comparison), encoding="utf-8")
    source_files = sorted(p for p in ROOT.rglob("*") if p.is_file()
                          and p.suffix in (".py", ".json", ".md", ".txt")
                          and "results" not in p.relative_to(ROOT).parts and "__pycache__" not in p.parts)
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in source_files}
    manifest = {"package_version": __version__, "executed_at_utc": datetime.now(timezone.utc).isoformat(),
                "python": platform.python_version(), "platform": platform.platform(),
                "execution_kind": "automated_validation", "independent_external_review": "outside_scope_of_automated_run",
                "dependencies": "Python standard library only", "source_inventory_sha256": digest(hashes),
                "source_sha256": hashes, "output_sha256": {name: sha(out / name) for name in STABLE_OUTPUTS},
                "test_transcript_sha256": sha(out / "test_results.txt")}
    write_json(out / "run_manifest.json", manifest)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))


if __name__ == "__main__":
    main()
