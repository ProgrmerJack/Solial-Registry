"""Shared source fingerprint and exact replay checks for derived audit files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def code_files():
    paths = sorted((ROOT / "src/social_registry").glob("*.py"))
    paths.append(ROOT / "scripts/run_analysis.py")
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def code_fingerprint():
    return hashlib.sha256(json.dumps(code_files(), sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def validated_audit(path):
    from .rules import LEGAL_SPEC, legal_audit
    data = json.loads(Path(path).read_text())
    spec_hash = hashlib.sha256(json.dumps(LEGAL_SPEC, sort_keys=True,
                              separators=(",", ":")).encode()).hexdigest()
    if data["reproducibility"]["input_sha256"] != spec_hash:
        raise ValueError("Audit input specification is stale")
    if data["reproducibility"]["code_sha256"] != code_fingerprint():
        raise ValueError("Audit code fingerprint is stale")
    if {k: v for k, v in data.items() if k != "reproducibility"} != legal_audit():
        raise ValueError("Audit contents disagree with exact replay")
    return data
