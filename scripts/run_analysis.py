#!/usr/bin/env python3
"""Run --self-test, --legal-audit, --demo, or --input compatible.json.
Results are diagnostics, not targeting accuracy or a 2027 scoring model.
"""
import argparse
from datetime import datetime, timezone
import hashlib,json,platform,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from social_registry.rules import LEGAL_SPEC,legal_audit
from social_registry.additive import evaluate
from social_registry.numeric import unique_object,invalid_constant
from social_registry.provenance import code_files,code_fingerprint
DEMO=json.loads((ROOT/"data/fixtures/additive_demo.json").read_text())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--demo", action="store_true")
    group.add_argument("--legal-audit", action="store_true")
    group.add_argument("--input", type=Path)
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    try:
        if args.legal_audit:
            raw = json.dumps(LEGAL_SPEC, sort_keys=True, separators=(",", ":")).encode()
            payload = None
            input_source = "data/rules/legal_specification.json; frozen constructed cases and labelled post-hoc review check"
        elif args.demo:
            raw = json.dumps(DEMO, sort_keys=True, separators=(",", ":")).encode()
            payload = DEMO
            input_source = "data/fixtures/additive_demo.json; explicitly synthetic fixture"
        else:
            raw = args.input.read_bytes()
            payload = json.loads(raw, object_pairs_hook=unique_object,
                                 parse_constant=invalid_constant)
            # Retain hash but do not expose potentially identifying input paths.
            input_source = "external input (path withheld)"
        report = legal_audit() if args.legal_audit else evaluate(payload)
        report["reproducibility"] = {
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "code_sha256": code_fingerprint(),
            "input_source": input_source,
            "python_version": platform.python_version(),
            "packages": "Python standard library only",
            "code_files_sha256": code_files(),
            "command": ["python", "scripts/run_analysis.py"] + (
                ["--legal-audit"] if args.legal_audit else
                ["--demo"] if args.demo else ["--input", "<same input bytes>"]),
            "run_utc": datetime.now(timezone.utc).isoformat(),
            "random_seed": None,
            "generation": "deterministic; no random sampling",
        }
        if args.legal_audit or args.demo:
            plan = ROOT / "docs/analysis_plan.md"
            report["reproducibility"]["analysis_plan_source"] = str(plan.relative_to(ROOT))
            report["reproducibility"]["analysis_plan_sha256"] = hashlib.sha256(plan.read_bytes()).hexdigest()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, TypeError, OSError, KeyError) as error:
        # Do not echo source data or raw identifiers in failure messages.
        print(f"validation failed: {type(error).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
