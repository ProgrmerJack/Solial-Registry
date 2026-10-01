#!/usr/bin/env python3
"""Render monochrome vector scientific figures from the verified audit."""
from fractions import Fraction
from pathlib import Path
import json,os,sys
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", "/tmp/social-registry-mpl")
sys.path.insert(0,str(ROOT/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from social_registry import rules
from social_registry.provenance import validated_audit
BLUE="0.05"
GREEN="0.35"
ORANGE="0.6"
GREY="0.15"

def figures(data):
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "normal", "axes.labelcolor": GREY,
                         "savefig.facecolor": "white"})
    names = []

    def save(fig, name):
        fig.savefig(out / (name + ".png"), dpi=220, bbox_inches="tight")
        fig.savefig(out / (name + ".pdf"), bbox_inches="tight",
                    metadata={"Title": "Exact constructed legal-rule diagnostic", "Author": "Author identity pending"})
        names.append(out / (name + ".png"))
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 3.5))
    intervals = [(3, 1, 2, "Special hardship income route", BLUE, False),
                 (2, 1, 1.5, "Intersection: ordinary-income reading", GREEN, False),
                 (1, 4/3, 2, "Intersection: adjusted-income reading", ORANGE, True)]
    for y, lo, hi, label, c, closed in intervals:
        ax.plot([lo, hi], [y, y], color=c, linewidth=8, solid_capstyle="butt")
        ax.scatter([lo], [y], color=c if closed else "white", edgecolors=c, s=85, zorder=3, linewidths=2)
        ax.scatter([hi], [y], color=c, s=85, zorder=3)
        ax.text(.87, y+.19, label, color=c, fontsize=10)
    ax.set(xlim=(.85, 2.1), ylim=(.5, 3.65), yticks=[],
           xticks=[1, 4/3, 1.5, 2], xticklabels=["1", "4/3", "3/2", "2"],
           xlabel="Ordinary monthly per-person income / P",
           title="The special route needs an explicit priority rule")
    ax.spines["left"].set_visible(False); ax.grid(axis="x", alpha=.2)
    fig.tight_layout(); save(fig, "01_hardship")

    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5))
    grid = data["extended_analysis"]["land_integer_grid"]
    for ax, summary in zip(axes.flat, data["extended_analysis"]["land_grid_summary"]):
        u = summary["total_m2"]
        rows = [r for r in grid if int(r["total_m2"]) == u]
        b = [int(r["buildings_m2"]) for r in rows]
        literal = [float(Fraction(r["literal_area_m2"])) for r in rows]
        proposed = [float(Fraction(r["proposed_zero_floor_area_m2"])) for r in rows]
        ax.axhline(0, color=GREY, linewidth=.8)
        ax.plot(b, literal, color=ORANGE, label="Literal rule", linewidth=2)
        ax.plot(b, proposed, color=GREEN, linestyle="--", label="Proposed floor", linewidth=1.7)
        ax.fill_between(b, literal, 0, where=[v < 0 for v in literal], color=ORANGE, alpha=.15)
        ax.set(title=f"U = {u:,} m² · {summary['negative_area_cases']} negative test cases",
               xlabel="Building area B (m²)", ylabel="Derived area L (m²)")
        ax.grid(alpha=.15)
    axes[0, 0].legend(fontsize=9)
    fig.suptitle("Constructed land domain, not cadastral observations", color=BLUE, weight="normal")
    fig.tight_layout(); save(fig, "02_land")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    wage = rules.LEGAL_SPEC["minimum_remuneration_monthly_soum"]
    xs = [Fraction(i, 100) for i in range(100, 301)]
    for ax, period in zip(axes, ["monthly", "three_month_total"]):
        for multiple, label, c in [(3, "Listed countries", BLUE), (2, "Other countries", GREEN)]:
            vals = [Fraction(rules.remittance_monthly(str(x*wage), wage, multiple, period)
                             ["monthly_contribution_soum"]) / wage for x in xs]
            # Draw separate sides: do not visually interpolate a discontinuous switch.
            for mask in [lambda x: x < 2, lambda x: x >= 2]:
                points = [(float(x), float(y)) for x, y in zip(xs, vals) if mask(x)]
                ax.plot(*zip(*points), color=c, linestyle="-" if multiple == 3 else "--", linewidth=1.5, label=label if mask(Fraction(1)) else None)
            at = Fraction(rules.remittance_monthly(2*wage, wage, multiple, period)["monthly_contribution_soum"]) / wage
            ax.scatter([2], [float(at)], color=c, s=35, zorder=4)
            ax.scatter([2], [multiple], facecolors="white", edgecolors=c, s=35, zorder=3)
        ax.axvline(2, color=GREY, linestyle="--", linewidth=1)
        ax.set(title="Monthly comparison" if period == "monthly" else "Three-month-total comparison",
               xlabel="Reported comparison quantity q / M", ylabel="Monthly contribution / M",
               ylim=(.5, 3.3)); ax.grid(alpha=.15)
    axes[0].legend(fontsize=9)
    fig.suptitle("Conditional period readings; official period unresolved", color=BLUE, weight="normal")
    fig.tight_layout(); save(fig, "03_remittances")

    return names


def main():
    data=validated_audit(ROOT/"results/audit/legal_rule_audit.json")
    paths=figures(data)
    print(json.dumps({"figures":[str(p.relative_to(ROOT)) for p in paths],"format":"monochrome PDF vectors and PNG previews"},indent=2))

if __name__=="__main__":
    main()
