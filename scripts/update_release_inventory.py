"""Refresh the release inventory after regenerating and validating results."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    listed = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=ROOT, check=True, capture_output=True).stdout.decode().split('\0')
    files = sorted({name for name in listed if name and (ROOT / name).is_file()
                    and name not in ('release-manifest.json', 'SHA256SUMS.txt')})
    summary = json.loads((ROOT / 'demonstrator/results/validation_summary.json').read_text(encoding='utf-8'))
    manifest = {
        'package_name': 'OGARD executable reference implementation', 'version': '0.2.0',
        'status': 'Executable Reference Release 0.2.0', 'release_date': '2026-09-23',
        'author': 'Deniz Bektas', 'website': 'https://denbek.github.io/ogard/',
        'repository': 'https://github.com/DenBek/ogard', 'public_release': True,
        'executed_selected_synthetic_results': True, 'full_benchmark_completed': False,
        'operator_adoption_claimed': False, 'independent_external_review_claimed': False,
        'contains_only_original_synthetic_or_public_material': True,
        'methodology_documents_version': 'Original Draft Release Candidate v0.1',
        'methodology_documents': sorted(p.name for p in (ROOT / 'papers').glob('*.pdf')),
        'tests_passed': summary['tests_passed'], 'source_layouts_verified': 2,
        'scenario_count': 5, 'decision_count': 6,
        'run_command': 'python run_validation.py --output ../ogard-rerun --verify-snapshot',
        'files': files,
    }
    (ROOT / 'release-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    entries = files + ['release-manifest.json']
    checksums = ''.join(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in sorted(entries))
    (ROOT / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
    print(json.dumps({'release_version':'0.2.0','checksummed_files':len(entries)}))


if __name__ == '__main__':
    main()
