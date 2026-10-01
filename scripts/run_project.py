#!/usr/bin/env python3
"""Reproduce computations, independent checks, exports, figures and XeLaTeX PDFs.

Run: .venv/bin/python scripts/run_project.py
Inputs under data/ are only read. Logs and generated outputs go under results/.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    python = str(ROOT/".venv/bin/python")
    logs = ROOT/"results/logs"
    logs.mkdir(exist_ok=True)
    stages = [
        ("legal_audit", [python,"scripts/run_analysis.py","--legal-audit"], "results/audit/legal_rule_audit.json"),
        ("synthetic_demo", [python,"scripts/run_analysis.py","--demo"], "results/audit/synthetic_validation.json"),
        ("tests", [python,"scripts/run_analysis.py","--self-test"], None),
        ("independent_algebra", [python,"scripts/verify_results.py"], None),
        ("csv_export", [python,"scripts/export_results.py"], None),
        ("figures", [python,"scripts/render_figures.py"], None),
        ("latex_documents", [python,"scripts/build_documents.py"], None),
    ]
    reports = []
    for name,command,target in stages:
        result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        log = logs/(name+".log")
        log.write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(f"Stage {name} failed ({result.returncode}); see {log}")
        if target:
            (ROOT/target).write_text(result.stdout)
        reports.append({"stage":name,"command":command,"cwd":str(ROOT),"exit_code":result.returncode,
                        "log":str(log.relative_to(ROOT)),"log_sha256":hashlib.sha256(log.read_bytes()).hexdigest()})
        print(f"{name}: PASS",flush=True)
    sources = [p for folder in ["src","scripts","tests"] for p in (ROOT/folder).rglob("*.py")]
    sources += list((ROOT/"data").rglob("*.json"))
    sources += list((ROOT/"docs").glob("*.md"))
    manifest = {"stages":reports,"source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}}
    (logs/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Execution manifest: results/logs/run_manifest.json")


if __name__=="__main__":
    main()
