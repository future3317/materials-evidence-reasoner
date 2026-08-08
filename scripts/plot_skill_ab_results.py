"""Create the publication-style two-model Skill A/B figure for the README.

The values are transcribed from docs/three-model-skill-ab-evaluation.md.
Only the comparable 0-100 Kimi-K2.7-Code and GLM-5.2 results are plotted;
the separate GPT-5.6-luna rubric is intentionally excluded.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


BLUE = "#3775BA"
GREEN = "#8BCF8B"
INK = "#272727"
GRID = "#D9D9D9"


def annotate_vertical(ax, bars, values: list[int]) -> None:
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.4,
            str(value),
            ha="center",
            va="bottom",
            fontsize=11,
            color=INK,
        )


def annotate_horizontal(ax, bars, values: list[int]) -> None:
    for bar, value in zip(bars, values, strict=True):
        x = bar.get_width()
        offset = 0.25 if value >= 0 else -0.25
        ha = "left" if value >= 0 else "right"
        ax.text(
            x + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+d}",
            ha=ha,
            va="center",
            fontsize=9.5,
            color=INK,
        )


def build_figure() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": ["Microsoft YaHei", "Arial", "DejaVu Sans"],
            "font.size": 10,
            "axes.linewidth": 1.2,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.unicode_minus": False,
            "legend.frameon": False,
            "svg.fonttype": "none",
        }
    )

    models = ["Kimi-K2.7-Code", "GLM-5.2"]
    baseline = [59, 58]
    skill = [75, 78]
    uplift = ["+16 分\n(+27.1%)", "+20 分\n(+34.5%)"]

    dimensions = [
        "科学正确性\n与证据可追溯",
        "抽取完整性\n与结构有效性",
        "单位、条件\n与归一化",
        "缺失、冲突\n与不确定性",
        "数据资产\n复用价值",
        "异常处理\n与复现性",
    ]
    kimi_delta = [5, 6, 4, 5, 3, 3]
    glm_delta = [10, 7, 5, 2, -2, -2]

    fig, (score_ax, delta_ax) = plt.subplots(
        1,
        2,
        figsize=(12.2, 5.4),
        gridspec_kw={"width_ratios": (0.95, 1.35)},
    )
    x = np.arange(len(models))
    width = 0.32
    baseline_bars = score_ax.bar(
        x - width / 2,
        baseline,
        width,
        label="无 Skill（基线）",
        color=BLUE,
        edgecolor=INK,
        linewidth=0.8,
    )
    skill_bars = score_ax.bar(
        x + width / 2,
        skill,
        width,
        label="有 Skill",
        color=GREEN,
        edgecolor=INK,
        linewidth=0.8,
    )
    annotate_vertical(score_ax, baseline_bars, baseline)
    annotate_vertical(score_ax, skill_bars, skill)
    for index, label in enumerate(uplift):
        score_ax.text(
            index,
            91.5,
            label,
            ha="center",
            va="center",
            fontsize=9.5,
            color=INK,
        )
    score_ax.set_title("(a) 总分对照", loc="left", fontsize=12, fontweight="bold", pad=12)
    score_ax.set_ylabel("加权得分（0–100）")
    score_ax.set_xticks(x, models)
    score_ax.set_ylim(0, 105)
    score_ax.set_yticks(np.arange(0, 101, 20))
    score_ax.grid(axis="y", color=GRID, linewidth=0.7)
    score_ax.set_axisbelow(True)
    score_ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.14),
        ncol=2,
        fontsize=9.5,
        handlelength=1.2,
        columnspacing=1.2,
    )

    y = np.arange(len(dimensions))
    height = 0.32
    kimi_bars = delta_ax.barh(
        y - height / 2,
        kimi_delta,
        height,
        label="Kimi-K2.7-Code",
        color=BLUE,
        edgecolor=INK,
        linewidth=0.8,
    )
    glm_bars = delta_ax.barh(
        y + height / 2,
        glm_delta,
        height,
        label="GLM-5.2",
        color=GREEN,
        edgecolor=INK,
        linewidth=0.8,
    )
    annotate_horizontal(delta_ax, kimi_bars, kimi_delta)
    annotate_horizontal(delta_ax, glm_bars, glm_delta)
    delta_ax.axvline(0, color=INK, linewidth=1.0)
    delta_ax.set_title("(b) 六维度增益", loc="left", fontsize=12, fontweight="bold", pad=12)
    delta_ax.set_xlabel("Skill − 基线（分）")
    delta_ax.set_yticks(y, dimensions)
    delta_ax.invert_yaxis()
    delta_ax.set_xlim(-4.5, 12.5)
    delta_ax.set_xticks(np.arange(-4, 13, 2))
    delta_ax.grid(axis="x", color=GRID, linewidth=0.7)
    delta_ax.set_axisbelow(True)
    delta_ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.14),
        ncol=2,
        fontsize=9.5,
        handlelength=1.2,
        columnspacing=1.2,
    )

    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.84, wspace=0.42)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/images/skill-ab-two-model-results.svg"),
        help="Output figure path (SVG, PNG, PDF, or another Matplotlib-supported format).",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure = build_figure()
    figure.savefig(args.output, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(figure)
    if args.output.suffix.lower() == ".svg":
        # Matplotlib wraps long path commands with indentation spaces; remove
        # only end-of-line whitespace so git diff --check stays clean.
        svg = args.output.read_text(encoding="utf-8")
        args.output.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")
    print(f"WROTE {args.output}")


if __name__ == "__main__":
    main()
