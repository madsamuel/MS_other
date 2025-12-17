#!/usr/bin/env python3
"""
dominant_persona_distribution.py

Purpose
-------
Build and plot a 100% user distribution across personas on Windows (or any OS)
using a Dominant-Persona Assignment Model derived from persona percentage ranges.

Key idea
--------
Your source data provides overlapping ranges (applicability), not a true population split.
To produce a 100% distribution, we must define an explicit dominant-persona rule and
a deterministic way to convert ranges into weights.

This script:
  1) Loads persona ranges (min%, max%)
  2) Computes a midpoint weight per persona
  3) Applies a dominant priority ordering (compute intensity) for presentation
  4) Normalizes weights so totals equal 100%
  5) Plots either a 100% stacked bar or a pie chart

Notes
-----
- The resulting distribution is a planning model, not an empirical measurement.
- "Mobile Worker" is often better treated as an overlay attribute. This script keeps it
  as a persona by default but allows you to treat it as an overlay (exclude from 100%).
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt


def build_default_source_data() -> List[Tuple[str, float, float]]:
    # Persona ranges from your table
    return [
        ("Kiosk User", 5, 50),
        ("Task Worker", 25, 80),
        ("Information Worker", 25, 80),
        ("Knowledge Worker", 10, 50),
        ("Power User", 5, 50),
        ("CAD/CAM Professional", 5, 25),
        ("Media Designer", 5, 50),
        ("Mobile Worker", 5, 80),
    ]


def build_default_priority() -> List[str]:
    # Dominant-persona ordering by compute intensity (highest first).
    # You can adjust this to match your organization's EUC definitions.
    return [
        "CAD/CAM Professional",
        "Media Designer",
        "Power User",
        "Knowledge Worker",
        "Information Worker",
        "Task Worker",
        "Kiosk User",
        "Mobile Worker",  # often treated as overlay; see --mobile-overlay
    ]


def validate_priority(priority: List[str], personas: List[str]) -> None:
    missing = [p for p in personas if p not in priority]
    extra = [p for p in priority if p not in personas]
    if missing or extra:
        msg = []
        if missing:
            msg.append(f"Priority missing personas: {missing}")
        if extra:
            msg.append(f"Priority contains unknown personas: {extra}")
        raise ValueError("Invalid priority list. " + " ".join(msg))


def compute_distribution(
    source_data: List[Tuple[str, float, float]],
    priority: List[str],
    mobile_overlay: bool = False,
) -> pd.DataFrame:
    df = pd.DataFrame(source_data, columns=["Persona", "MinPercent", "MaxPercent"])

    if mobile_overlay:
        df = df[df["Persona"] != "Mobile Worker"].copy()

    personas = df["Persona"].tolist()
    validate_priority(priority, personas)

    # Midpoint weight (transparent, deterministic)
    df["Midpoint"] = (df["MinPercent"] + df["MaxPercent"]) / 2.0

    # Priority for sorting (presentation order)
    df["Priority"] = df["Persona"].apply(lambda p: priority.index(p))
    df = df.sort_values("Priority", ascending=True)

    # Normalize to 100%
    total = df["Midpoint"].sum()
    if total <= 0:
        raise ValueError("Total midpoint weight is not positive; cannot normalize.")

    df["NormalizedPercent"] = df["Midpoint"] / total * 100.0

    # Round for display while preserving original numeric column if needed
    df["NormalizedPercentRounded"] = df["NormalizedPercent"].round(2)

    # Keep only useful columns (but keep Midpoint in case you want to audit)
    df = df[["Persona", "MinPercent", "MaxPercent", "Midpoint", "NormalizedPercent", "NormalizedPercentRounded"]]
    return df


def plot_stacked_bar(df: pd.DataFrame, title_suffix: str = "") -> None:
    labels = df["Persona"].tolist()
    values = df["NormalizedPercent"].tolist()

    # Professional color palette - soft, modern colors
    colors = [
        '#5B9BD5',  # Blue
        '#70AD47',  # Green
        '#FFC000',  # Amber
        '#ED7D31',  # Orange
        '#A5A5A5',  # Gray
        '#4472C4',  # Deep Blue
        '#C55A11',  # Rust
        '#7030A0',  # Purple
    ]

    fig, ax = plt.subplots(figsize=(12, 3.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    left = 0.0
    for i, (label, value) in enumerate(zip(labels, values)):
        ax.barh(y=["Persona"], width=[value], left=[left], 
                label=f"{label} ({value:.1f}%)", 
                color=colors[i % len(colors)],
                edgecolor='white', linewidth=0.5)
        left += float(value)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentage of IT Workforce", fontsize=11)
    ax.set_title(
        "100% User Distribution by Dominant Persona\n"
        f"(Derived from persona ranges using midpoint normalization){title_suffix}",
        fontsize=12, pad=15
    )
    ax.legend(bbox_to_anchor=(0.5, -0.2), loc="upper center", borderaxespad=0.0, 
              frameon=True, fancybox=False, shadow=False, ncol=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.subplots_adjust(bottom=0.3)
    plt.show()


def plot_pie(df: pd.DataFrame, title_suffix: str = "") -> None:
    labels = df["Persona"].tolist()
    values = df["NormalizedPercent"].tolist()

    # Professional color palette - soft, modern colors
    colors = [
        '#5B9BD5',  # Blue
        '#70AD47',  # Green
        '#FFC000',  # Amber
        '#ED7D31',  # Orange
        '#A5A5A5',  # Gray
        '#4472C4',  # Deep Blue
        '#C55A11',  # Rust
        '#7030A0',  # Purple
    ]

    fig = plt.figure(figsize=(8.5, 8.5))
    fig.patch.set_facecolor('white')
    
    plt.pie(values, labels=labels, autopct="%1.0f%%", startangle=90,
            colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            textprops={'fontsize': 10})
    plt.title(
        "User Distribution by Dominant Persona\n"
        f"(Derived from persona ranges using midpoint normalization){title_suffix}",
        fontsize=12, pad=20
    )
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot a 100% dominant-persona distribution derived from overlapping persona ranges."
    )
    parser.add_argument(
        "--chart",
        choices=["stacked", "pie", "both"],
        default="stacked",
        help="Which chart to plot.",
    )
    parser.add_argument(
        "--mobile-overlay",
        action="store_true",
        help="Treat Mobile Worker as an overlay attribute (exclude it from the 100%% distribution).",
    )
    parser.add_argument(
        "--print-table",
        action="store_true",
        help="Print the computed distribution table to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    source_data = build_default_source_data()
    priority = build_default_priority()

    df = compute_distribution(
        source_data=source_data,
        priority=priority,
        mobile_overlay=args.mobile_overlay,
    )

    title_suffix = ""
    if args.mobile_overlay:
        title_suffix = " and Mobile Worker treated as overlay (excluded)"

    if args.print_table:
        # Print a concise audit table
        out = df.copy()
        out["MinPercent"] = out["MinPercent"].map(lambda x: f"{x:.0f}%")
        out["MaxPercent"] = out["MaxPercent"].map(lambda x: f"{x:.0f}%")
        out["Midpoint"] = out["Midpoint"].map(lambda x: f"{x:.1f}")
        out["NormalizedPercent"] = out["NormalizedPercent"].map(lambda x: f"{x:.2f}%")
        print(out.to_string(index=False))

    if args.chart in ("stacked", "both"):
        plot_stacked_bar(df, title_suffix=title_suffix)

    if args.chart in ("pie", "both"):
        plot_pie(df, title_suffix=title_suffix)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
