import argparse
import json
from pathlib import Path
from .io import read_json


def main():
    parser = argparse.ArgumentParser(description="Focused OGARD synthetic demonstrator")
    sub = parser.add_subparsers(dest="command", required=True)
    process = sub.add_parser("process")
    process.add_argument("--input", required=True)
    process.add_argument("--output", required=True)
    normalize = sub.add_parser("normalize")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--mapping", required=True)
    normalize.add_argument("--output", required=True)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--input", required=True)
    baseline.add_argument("--output", required=True)
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--decisions", required=True)
    evaluate.add_argument("--expectations", required=True)
    evaluate.add_argument("--output", required=True)
    report = sub.add_parser("report")
    report.add_argument("--decisions", required=True)
    report.add_argument("--evaluation", required=True)
    report.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "process":
        from .engine import process_document
        result = process_document(read_json(args.input))
    elif args.command == "normalize":
        from .adapters import normalize_layout_b
        result = normalize_layout_b(read_json(args.input), read_json(args.mapping))
    elif args.command == "baseline":
        from .baseline import process_baseline, without_reviews
        result = process_baseline(without_reviews(read_json(args.input)))
    elif args.command == "evaluate":
        from .evaluate import evaluate_document
        result = evaluate_document(read_json(args.decisions), read_json(args.expectations))
    else:
        from .report import render_report
        result = render_report(read_json(args.decisions), read_json(args.evaluation))
    output.write_text(result if isinstance(result, str) else json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.command == "evaluate" and not result["all_workflow_checks_passed"]:
        raise SystemExit("Evaluation found a workflow or integrity discrepancy; inspect " + str(output))
    print(str(output))


if __name__ == "__main__":
    main()
