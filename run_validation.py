"""Run the complete OGARD release validation without altering supplied results."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
STABLE_OUTPUTS = ("decisions.json", "automatic_decisions.json", "baseline_decisions.json", "evaluation.json",
                  "comparison.json", "comparison.md", "layout_b_normalized.json", "adaptation.json",
                  "walkthrough.html", "validation_summary.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.duplicate_ids = [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicate_ids.append(attrs["id"])
            self.ids.add(attrs["id"])
        for field in ("href", "src"):
            if field in attrs:
                self.links.append(attrs[field])


def check_local_links():
    parsed = {}
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in (".git", ".venv", "__pycache__") for part in path.relative_to(ROOT).parts):
            continue
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.duplicate_ids:
            raise ValueError(str(path.relative_to(ROOT)) + ": duplicate HTML IDs")
        parsed[path] = parser
    checked = 0
    for path, parser in parsed.items():
        for target in parser.links:
            url = urlsplit(target)
            if url.scheme or url.netloc or not target or target.startswith("/"):
                continue
            destination = (path.parent / unquote(url.path)).resolve() if url.path else path
            if destination.is_dir():
                destination = destination / "index.html"
            if ROOT != destination and ROOT not in destination.parents:
                raise ValueError("Local link escapes repository: " + target)
            if not destination.is_file():
                raise ValueError(str(path.relative_to(ROOT)) + ": missing " + target)
            if url.fragment and destination.suffix == ".html":
                if destination not in parsed or unquote(url.fragment) not in parsed[destination].ids:
                    raise ValueError(str(path.relative_to(ROOT)) + ": missing fragment " + target)
            checked += 1
    return {"html_files": len(parsed), "local_references_checked": checked}


def verify_checksums():
    count = 0
    names = set()
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        if name in names or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Invalid checksum inventory entry: " + name)
        names.add(name)
        path = (ROOT / name).resolve()
        if ROOT not in path.parents or not path.is_file() or sha(path) != expected:
            raise ValueError("Release checksum mismatch: " + name)
        count += 1
    if not count:
        raise ValueError("Empty release checksum inventory")
    manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    if names != set(manifest["files"]) | {"release-manifest.json"}:
        raise ValueError("Release manifest and checksum inventory differ")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent / "ogard-validation")
    parser.add_argument("--verify-snapshot", action="store_true")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or later is required")
    out = args.output.resolve()
    if ROOT == out or ROOT in out.parents:
        raise SystemExit("Choose an output directory outside the repository to preserve the supplied release")
    result = subprocess.run([sys.executable, str(ROOT / "demonstrator/run_demo.py"), "--output", str(out)],
                            cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(result.returncode)
    summary = json.loads(result.stdout)
    links = check_local_links()
    snapshot_count = checksum_count = 0
    if args.verify_snapshot:
        for name in STABLE_OUTPUTS:
            if sha(out / name) != sha(ROOT / "demonstrator/results" / name):
                raise ValueError("Supplied output differs: " + name)
            snapshot_count += 1
        supplied = json.loads((ROOT / "demonstrator/results/run_manifest.json").read_text(encoding="utf-8"))
        current = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
        if current["source_sha256"] != supplied["source_sha256"]:
            raise ValueError("Supplied run used different implementation source files")
        checksum_count = verify_checksums()
    record = {"release_version": summary["release_version"], "all_checks_passed": True,
              "tests_passed": summary["tests_passed"], "tests_failed": summary["tests_failed"],
              "source_layouts_verified": summary["source_layouts_verified"],
              "deterministic_outputs_verified": snapshot_count, "release_files_checksum_verified": checksum_count,
              "snapshot_verification_requested": args.verify_snapshot, "website": links,
              "independent_external_review": "outside_scope_of_automated_run"}
    (out / "release_validation.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
