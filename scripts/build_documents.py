#!/usr/bin/env python3
"""Compile maintained Uzbek, Russian and English justification and submission sources.

Maintained publication text is in docs/*.tex; each source is standalone.
Formatting basis: O‘RQ-682 drafting-methodology §§43–51 and §§83–85.
No official LaTeX class or exact Times New Roman font is claimed.
"""
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from social_registry.provenance import validated_audit

ESCAPES = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
           "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
           "≤": r"\ensuremath{\leq}", "≥": r"\ensuremath{\geq}",
           "Σ": r"\ensuremath{\Sigma}", "×": r"\ensuremath{\times}",
           "⇔": r"\ensuremath{\Longleftrightarrow}", "→": r"\ensuremath{\rightarrow}",
           "∈": r"\ensuremath{\in}", "ⱼ": r"\textsubscript{j}",
           "₀": r"\textsubscript{0}"}

MATH = {
    "D = Y/(3N)": r"$D=Y/(3N)$",
    "A = 3D/4": r"$A=\frac{3}{4}D$",
    "L = U − B − min(U/5, 200)": r"$L=U-B-\min\{U/5,200\}$",
    "E = max(2.5T/3, B₀)": r"$E=\max\{5T/6,B_0\}$",
    "G = max(0.07g − 1, 0) × 0.5M": r"$G=\max\{0.07g-1,0\}M/2$",
    "S = Σwⱼzⱼ": r"$S=\sum_j w_jz_j$",
    "L = Σmin(wⱼaⱼ,wⱼbⱼ)": r"$L=\sum_j\min(w_ja_j,w_jb_j)$",
    "U = Σmax(wⱼaⱼ,wⱼbⱼ)": r"$U=\sum_j\max(w_ja_j,w_jb_j)$",
}


def escape(text):
    # Substitutions are authored typographical equivalents, not a new calculation.
    pattern = "(" + "|".join(re.escape(k) for k in sorted(MATH, key=len, reverse=True)) + ")"
    parts = re.split(pattern, text)
    return "".join(MATH[p] if p in MATH else "".join(ESCAPES.get(c, c) for c in p)
                   for p in parts)


def numeric_text(value):
    f = Fraction(str(value))
    return f"{f.numerator:,}" if f.denominator == 1 else f"{f.numerator:,}/{f.denominator}"


def result_table(headers, rows):
    n = len(headers)
    spec = " ".join([rf"p{{\dimexpr\linewidth/{n}-2\tabcolsep\relax}}"] * n)
    out = "\\begingroup\\fontsize{11}{13.2}\\selectfont\n\\begin{longtable}{" + spec + "}\n\\toprule\n"
    out += " & ".join(escape(h) for h in headers) + r" \\" + "\n\\midrule\n\\endhead\n"
    for row in rows:
        out += " & ".join(escape(str(cell)) for cell in row) + r" \\" + "\n"
    return out + "\\bottomrule\n\\end{longtable}\n\\endgroup\n"


def export_tex_tables(audit):
    e = audit["extended_analysis"]
    land = [[numeric_text(r[k]) for k in ["total_m2", "constructed_cases", "negative_area_cases", "minimum_literal_area_m2", "maximum_zero_floor_monthly_income_change_soum"]]
            for r in e["land_grid_summary"]]
    land.append(["Total constructed grid", numeric_text(len(e["land_integer_grid"])),
                 numeric_text(sum(r["negative_area_cases"] for r in e["land_grid_summary"])), "—", "—"])
    (ROOT/"results/tables/land_summary.tex").write_text(result_table(
        ["Plot U (m²)", "Integer test cases", "Negative cases", "Minimum L (m²)", "Maximum floor change (soum/month)"], land))
    remittance = [["Monthly" if r["interpretation"] == "monthly" else "Three-month total",
                   "Listed countries" if r["country_group"] == "listed_countries" else "Other countries",
                   numeric_text(r["drop_at_comparison_threshold_monthly_soum"]),
                   numeric_text(r["drop_per_person_four_members_soum"])]
                   for r in e["conditional_remittance_threshold_drops"]]
    (ROOT/"results/tables/remittance_summary.tex").write_text(result_table(
        ["Conditional period", "Country group", "Monthly contribution drop (soum)", "Per-person drop, four members (soum)"], remittance))
    labels = {"Tashkent": "Tashkent", "Nukus_and_regional_centres": "Nukus / regional centres",
              "other_cities": "Other cities", "other_administrative_units": "Other units"}
    coefficient = []
    for r in audit["self_employment_coefficient_comparison"]:
        extra = [next(x["informal_monthly_soum"] for x in e["informal_income_cases"]
                      if x["region_class"] == r["region_class"] and x["sex"] == sex)
                 for sex in ("male", "female")]
        coefficient.append([labels[r["region_class"]]] + [numeric_text(r[k]) for k in
            ["male_monthly_normative_income_soum", "female_monthly_normative_income_soum"]] + [numeric_text(x) for x in extra])
    (ROOT/"results/tables/coefficient_summary.tex").write_text(result_table(
        ["Geographic class", "Male base", "Female base", "Informal male", "Informal female"], coefficient))


DOCUMENT_NAMES = (
    "normative_act_draft_ru", "explanatory_note_ru", "research_paper_ru",
    "participation_request_ru",
    "normative_act_draft_uz", "explanatory_note_uz", "research_paper_uz",
    "participation_request_uz",
    "normative_act_draft_en", "explanatory_note_en", "research_paper",
    "participation_request_en",
)


def checked_sources():
    """Read every maintained source; this check does not write to any file."""
    paths = []
    for name in DOCUMENT_NAMES:
        path = ROOT/"docs"/(name+".tex")
        source = path.read_text()
        if "\\begin{document}" not in source or "\\end{document}" not in source:
            raise ValueError(f"Incomplete source: {path}")
        paths.append(path)
    return paths


def compiler_environment():
    """Add the vendored packages in tex/ (ulem, Russian babel), retaining default search paths."""
    environment = os.environ.copy()
    environment["TEXINPUTS"] = (
        str(ROOT / "tex") + "//" + os.pathsep
        + environment.get("TEXINPUTS", "") + os.pathsep
    )
    return environment


def build():
    paths = checked_sources()
    audit = validated_audit(ROOT/"results/audit/legal_rule_audit.json")
    export_tex_tables(audit)
    output = ROOT/"results/documents"
    logs = ROOT/"results/logs"
    output.mkdir(exist_ok=True); logs.mkdir(exist_ok=True)
    reports = {}
    for path in paths:
        name = path.stem
        command = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
                   "-output-directory="+str(output), name+".tex"]
        for run in (1,2):
            result = subprocess.run(command, cwd=ROOT/"docs", capture_output=True, text=True,
                                    env=compiler_environment())
            (logs/f"{name}_xelatex_{run}.log").write_text(result.stdout+result.stderr)
            if result.returncode:
                raise RuntimeError(f"XeLaTeX failed for {name}; see results/logs/{name}_xelatex_{run}.log")
        pdf = output/f"{name}.pdf"
        pages = PdfReader(pdf).pages
        text = "\n".join(page.extract_text() for page in pages)
        if name == "research_paper" and not all(n in text for n in ["4,105", "620", "Results", "References"]):
            raise ValueError("Research PDF is missing required results or sections")
        if "Missing character:" in result.stdout:
            raise ValueError(f"Missing font glyph in {name}")
        if re.search(r"Overfull \\[hv]box", result.stdout):
            raise ValueError(f"Typesetting overflow in {name}; inspect the log")
        reports[name] = {"pages": len(pages), "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                         "tex_sha256": hashlib.sha256((ROOT/"docs"/(name+".tex")).read_bytes()).hexdigest(),
                         "command": command}
    manifest = {"engine": subprocess.run(["xelatex", "--version"],capture_output=True,text=True).stdout.splitlines()[0],
                "font": "Liberation Serif; disclosed Times-compatible substitution",
                "draft_format_basis": "O‘RQ-682 appended methodology §§43–51",
                "documents": reports,
                "python_dependencies": {p:importlib.metadata.version(p) for p in ["pypdf"]}}
    (logs/"document_build_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compile maintained LaTeX sources without regenerating or overwriting them.")
    parser.add_argument("--check-sources", action="store_true", help="Validate source presence without compiling or writing any output.")
    args = parser.parse_args()
    if args.check_sources:
        for path in checked_sources():
            print(path.stem + ": " + hashlib.sha256(path.read_bytes()).hexdigest())
    else:
        build()
