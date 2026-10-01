#!/usr/bin/env python3
"""Compile maintained Uzbek, Russian and English justification and submission sources.

Maintained publication text is in docs/*.tex. Earlier Markdown inputs are
retained as drafting inputs; a normal build never regenerates TeX from them.
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

from bs4 import BeautifulSoup, NavigableString
import markdown
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


def inline(node, refs=None):
    if isinstance(node, NavigableString):
        return escape(str(node))
    content = "".join(inline(c, refs) for c in node.children)
    if node.name in ("strong", "b"):
        return r"\textbf{" + content + "}"
    if node.name in ("em", "i"):
        return r"\emph{" + content + "}"
    if node.name == "code":
        raw = node.get_text()
        if "/" in raw and re.fullmatch(r"[A-Za-z0-9_./-]+", raw) and re.search(r"[A-Za-z]", raw):
            return r"\nolinkurl{" + raw + "}"
        return r"\texttt{" + content + "}"
    if node.name == "a":
        url = node.get("href", "")
        if refs and url in refs:
            return r"\cite{" + refs[url] + "}"
        return r"\href{" + url.replace("%", r"\%") + "}{" + content + "}"
    if node.name == "br":
        return r"\\"
    return content


def generic_table(node):
    rows = node.find_all("tr")
    n = len(rows[0].find_all(["th", "td"], recursive=False))
    spec = " ".join([rf"p{{\dimexpr\linewidth/{n}-2\tabcolsep\relax}}"] * n)
    parts = ["\\begingroup\n\\fontsize{11}{13.2}\\selectfont\n",
             r"\begin{longtable}{" + spec + "}\n\\toprule\n"]
    for i, row in enumerate(rows):
        cells = [inline(c) for c in row.find_all(["th", "td"], recursive=False)]
        parts.append(" & ".join(cells) + r" \\" + "\n")
        if i == 0:
            parts.append("\\midrule\n\\endhead\n")
    parts.append("\\bottomrule\n\\end{longtable}\n\\endgroup\n")
    return "".join(parts)


def convert(text, refs=None, scientific=False, legal=False):
    soup = BeautifulSoup(markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"]), "html.parser")
    output = []
    table = 0
    for node in soup.children:
        if isinstance(node, NavigableString):
            continue
        name = node.name
        if name in ("h1", "h2", "h3", "h4"):
            title = node.get_text()
            title = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", title)
            if title.startswith("Appendix A."):
                output.append("\\appendix\n")
                title = title.partition(". ")[2]
            elif title.startswith("Appendix B."):
                title = title.partition(". ")[2]
            cmd = "section" if name in ("h1", "h2") else "subsection"
            if not scientific:
                cmd += "*"
            output.append("\\" + cmd + "{" + escape(title) + "}\n")
        elif name == "p":
            image = node.find("img")
            if image:
                path = Path(image["src"]).with_suffix(".pdf")
                output.append("\\begin{center}\n\\includegraphics[width=0.96\\linewidth]{" + path.as_posix() + "}\n\\end{center}\n")
            elif node.get_text().startswith("D > P and (3/4)D"):
                output.append("\\begin{equation}\n D>P,\\quad\\frac34D\\leq\\frac32P"
                              "\\quad\\Longleftrightarrow\\quad P<D\\leq2P.\n\\end{equation}\n")
            else:
                output.append(inline(node, refs) + "\n\n")
        elif name in ("ol", "ul"):
            environment = "enumerate" if name == "ol" else "itemize"
            start = int(node.get("start", 1))
            if legal and name == "ol":
                for index, li in enumerate(node.find_all("li", recursive=False), start):
                    output.append(r"\noindent\hspace*{1.27cm}" + str(index) + ". " + inline(li, refs).strip() + "\\par\n")
                continue
            options = f"[start={start}]" if name == "ol" else ""
            output.append("\\begin{" + environment + "}" + options + "\n")
            for li in node.find_all("li", recursive=False):
                output.append("\\item " + inline(li, refs) + "\n")
            output.append("\\end{" + environment + "}\n")
        elif name == "blockquote":
            output.append("\\begin{quote}\n" + inline(node, refs) + "\n\\end{quote}\n")
        elif name == "pre":
            output.append("\\begingroup\\fontsize{11}{13.2}\\selectfont\n\\begin{verbatim}\n" + node.get_text() + "\\end{verbatim}\n\\endgroup\n")
        elif name == "table":
            table += 1
            if scientific and table <= 3:
                output.append(r"\input{../results/tables/" + ["land_summary.tex", "remittance_summary.tex", "coefficient_summary.tex"][table-1] + "}\n")
            else:
                output.append(generic_table(node))
        else:
            raise ValueError(f"Unsupported document element: {name}")
    return "".join(output)


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


def preamble(size=12, draft=False):
    prefix = rf"\documentclass[{size}pt,a4paper]{{extarticle}}" + "\n"
    prefix += r"""\usepackage[left=3cm,right=2cm,top=2cm,bottom=2cm,headheight=18pt]{geometry}
\usepackage{fontspec}
\setmainfont{Liberation Serif}
\setsansfont{Liberation Serif}
\setmonofont[Scale=0.82]{Liberation Mono}
\usepackage{unicode-math}
\setmathfont{texgyretermes-math.otf}
\usepackage{amsmath,graphicx,booktabs,longtable,array,enumitem}
\usepackage{titlesec,fancyhdr}
\usepackage[hidelinks,unicode]{hyperref}
\usepackage{url}
\urlstyle{same}
\setlength{\parindent}{1.27cm}
\setlength{\parskip}{0pt}
\linespread{1}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\titleformat{\section}{\normalfont\bfseries}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalfont\bfseries}{\thesubsection.}{0.5em}{}
\titlespacing*{\section}{0pt}{1.2em}{0.5em}
\titlespacing*{\subsection}{0pt}{0.9em}{0.3em}
\setlist{nosep,leftmargin=1.27cm}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[C]{\ifnum\value{page}>1\thepage\fi}
% Liberation Serif is a disclosed Times-compatible substitute, not Times New Roman.
% Current statutory geometry/size baseline: O‘RQ-682 appendix §§43–51.
"""
    if draft:
        prefix += "\\hyphenpenalty=10000\n\\exhyphenpenalty=10000\n"
        prefix += "\\pretolerance=10000\n\\tolerance=10000\n\\setlength{\\emergencystretch}{4em}\n"
        prefix += "\\renewcommand{\\normalsize}{\\fontsize{14bp}{16.8bp}\\selectfont}\n\\normalsize\n"
    return prefix + "\\begin{document}\n"


def write_sources(audit):
    """Prevent legacy Markdown regeneration from replacing maintained editor sources."""
    raise RuntimeError("LaTeX sources are maintained directly; source regeneration is disabled.")


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
    """Use installed project-local TeX packages, retaining default search paths."""
    environment = os.environ.copy()
    local_packages = ROOT / ".venv/share/texmf/tex"
    if local_packages.is_dir():
        environment["TEXINPUTS"] = (
            str(local_packages) + "//" + os.pathsep
            + environment.get("TEXINPUTS", "") + os.pathsep
        )
    return environment


def build():
    paths = checked_sources()
    audit = validated_audit(ROOT/"results/audit/legal_rule_audit.json")
    export_tex_tables(audit)
    # The editor's .tex sources are authoritative. Never replace author edits
    # with the earlier Markdown conversion during a normal publication build.
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
                "python_dependencies": {p:importlib.metadata.version(p) for p in ["markdown","beautifulsoup4","pypdf"]}}
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
