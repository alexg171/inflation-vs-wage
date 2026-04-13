"""
analysis.py — Generates publication-ready charts for the Substack article:
  "Have Wages Kept Up With Inflation?"

Produces:
  images/chart1_wages_vs_cpi.png  — Nominal wages, CPI, real wages indexed to Jan 2019
  images/chart2_cpi_categories.png — % change per CPI category vs wage growth (bar chart)

Run:
  cd src
  python analysis.py

  For Chart 2, prepared_cpi_data.csv must exist in data/.
  If it doesn't, run:  python prepare_cpi_data.py --start_date 2019 --end_date 2024
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
IMG_DIR = os.path.join(ROOT, "images")
os.makedirs(IMG_DIR, exist_ok=True)

WAGE_CSV = os.path.join(DATA_DIR, "wage_vs_inflation.csv")
CPI_CSV  = os.path.join(DATA_DIR, "prepared_cpi_data.csv")

# ── style ──────────────────────────────────────────────────────────────────────
BLUE   = "#2563EB"
RED    = "#DC2626"
GREEN  = "#16A34A"
GRAY   = "#6B7280"
LIGHT  = "#F3F4F6"

plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        12,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.color":       "#E5E7EB",
    "grid.linewidth":   0.8,
    "figure.dpi":       150,
})

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Wages vs CPI (indexed, Jan 2019 = 100)
# ══════════════════════════════════════════════════════════════════════════════

def chart1_wages_vs_cpi():
    df = pd.read_csv(WAGE_CSV, index_col=0, parse_dates=True)

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(df.index, df["WAGES_IDX"], color=BLUE,  linewidth=2.2, label="Nominal Wages")
    ax.plot(df.index, df["CPI_IDX"],   color=RED,   linewidth=2.2, label="CPI (Inflation)")
    ax.plot(df.index, df["Real Wages"],color=GREEN,  linewidth=2.2, label="Real Wages", linestyle="--")

    # Baseline
    ax.axhline(100, color=GRAY, linewidth=1, linestyle=":")

    # Annotate the inflation peak (Jun 2022 — CPI peaked)
    peak_date = df["CPI_IDX"].idxmax()
    peak_val  = df.loc[peak_date, "CPI_IDX"]
    ax.annotate(
        f"Inflation peak\n{peak_date.strftime('%b %Y')}",
        xy=(peak_date, peak_val),
        xytext=(peak_date - pd.DateOffset(months=14), peak_val + 2),
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.4),
        color=RED, fontsize=10, ha="center",
    )

    # Final values annotation (right edge)
    last = df.index[-1]
    for col, color, label in [
        ("WAGES_IDX",  BLUE,  "Nominal"),
        ("CPI_IDX",    RED,   "CPI"),
        ("Real Wages", GREEN, "Real"),
    ]:
        val = df.loc[last, col]
        ax.text(last + pd.DateOffset(days=20), val, f"{val:.1f}", color=color,
                fontsize=9.5, va="center", fontweight="bold")

    ax.set_title("Have Wages Kept Up With Inflation?",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("Index  (Jan 2019 = 100)", fontsize=11)
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)

    # Footnote
    fig.text(0.01, 0.01,
             "Source: BLS — Average Hourly Earnings (CES0500000003) & CPI-U (CPIAUCSL).  Jan 2019 = 100.",
             fontsize=8, color=GRAY)

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out = os.path.join(IMG_DIR, "chart1_wages_vs_cpi.png")
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Saved → {out}")

    # Print key stats
    wage_pct  = df["WAGES_IDX"].iloc[-1]  - 100
    cpi_pct   = df["CPI_IDX"].iloc[-1]   - 100
    real_pct  = df["Real Wages"].iloc[-1] - 100
    print(f"\n  Nominal wage growth (Jan 2019 – Dec 2024): +{wage_pct:.1f}%")
    print(f"  CPI growth:                                 +{cpi_pct:.1f}%")
    print(f"  Real wage change:                           {real_pct:+.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — CPI Categories vs Wage Growth (horizontal bar)
# ══════════════════════════════════════════════════════════════════════════════

# Group labels for color-coding
CATEGORY_GROUPS = {
    "Food & Beverage": ["Food Bev", "Food at Home", "Cereals Bakery", "Meats Poultry Fish Eggs",
                        "Fruits Veg", "Nonalc Bev", "Other Food at Home", "Dairy",
                        "Food Away Home", "Full Service Meals", "Limited Service Meals"],
    "Energy":          ["Energy", "Gasoline", "Electricity", "Utility Gas"],
    "Housing":         ["Housing", "Shelter"],
    "Medical":         ["Medical Care", "Hospital Services", "Physicians Services", "Prescription Drugs"],
    "Transportation":  ["Transportation", "New Vehicles", "Used Cars Trucks"],
    "Other":           ["Less Food Energy", "Apparel", "Recreation", "Education", "Communication"],
}

GROUP_COLORS = {
    "Food & Beverage": "#F59E0B",
    "Energy":          "#EF4444",
    "Housing":         "#8B5CF6",
    "Medical":         "#06B6D4",
    "Transportation":  "#10B981",
    "Other":           "#6B7280",
}

def _get_group(name):
    for group, members in CATEGORY_GROUPS.items():
        if name in members:
            return group
    return "Other"


def chart2_cpi_categories():
    if not os.path.exists(CPI_CSV):
        print(f"\n  {CPI_CSV} not found.")
        print("   Run:  python prepare_cpi_data.py --start_date 2019 --end_date 2024")
        print("   Then re-run this script.")
        return

    df = pd.read_csv(CPI_CSV, index_col="Date", parse_dates=True)

    start = df.index.min()
    end   = df.index.max()

    # % change from first to last for each CPI category
    pct = {}
    for col in df.columns:
        series = df[col].dropna()
        if len(series) < 2:
            continue
        pct[col] = (series.iloc[-1] / series.iloc[0] - 1) * 100

    # Wage growth over same period
    wage_df = pd.read_csv(WAGE_CSV, index_col=0, parse_dates=True)
    w = wage_df.loc[start:end, "Wages"]
    wage_growth = (w.iloc[-1] / w.iloc[0] - 1) * 100

    # Overall inflation = "All Items" CPI (the divergence baseline)
    inflation_rate = pct.get("All Items", None)
    if inflation_rate is None:
        print("  'All Items' column not found in prepared_cpi_data.csv — cannot set baseline.")
        return

    # Add wages as an entry
    pct["Wages"] = wage_growth

    # Sort by absolute % change ascending (smallest at top, largest at bottom)
    pct_df = pd.Series(pct).sort_values(ascending=True)

    # Build chart
    n = len(pct_df)
    fig, ax = plt.subplots(figsize=(11, max(9, n * 0.40)))

    categories = pct_df.index.tolist()
    abs_vals   = pct_df.values
    rel_vals   = [v - inflation_rate for v in abs_vals]

    # Color: red if outpaced inflation, green if lagged; Wages gets blue; All Items gets gray
    bar_colors = []
    for c, rv in zip(categories, rel_vals):
        if c == "All Items":
            bar_colors.append(GRAY)
        elif c == "Wages":
            bar_colors.append(BLUE)
        elif rv > 0:
            bar_colors.append("#EF4444")   # outpaced inflation — bad for consumers
        else:
            bar_colors.append("#16A34A")   # lagged inflation — better for consumers

    bars = ax.barh(categories, abs_vals, color=bar_colors, alpha=0.85, height=0.72)

    # Inflation and wage reference lines
    ax.axvline(inflation_rate, color=GRAY, linewidth=1.8, linestyle="--", zorder=3)
    ax.axvline(wage_growth,    color=BLUE, linewidth=1.8, linestyle="--", zorder=3)

    # Value labels
    for bar, abs_val in zip(bars, abs_vals):
        ax.text(abs_val + 0.4, bar.get_y() + bar.get_height() / 2,
                f"{abs_val:.1f}%", va="center", ha="left", fontsize=8.5, color="#111827")

    # Legend
    legend_handles = [
        mpatches.Patch(color="#EF4444", alpha=0.85, label="Outpaced inflation"),
        mpatches.Patch(color="#16A34A", alpha=0.85, label="Below inflation"),
        mpatches.Patch(color=BLUE,      alpha=0.85, label=f"Wages ({wage_growth:.1f}%)"),
        plt.Line2D([0], [0], color=GRAY, linewidth=1.8, linestyle="--",
                   label=f"Overall inflation ({inflation_rate:.1f}%)"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9, framealpha=0.92)

    ax.set_title(
        "Price Change by Category vs. Overall Inflation",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_xlabel("% Change", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_xlim(left=0)

    # Subtitle
    fig.text(0.5, 0.985,
             f"{start.strftime('%b %Y')} - {end.strftime('%b %Y')}  |  Labels show absolute % change",
             ha="center", fontsize=9.5, color=GRAY, style="italic")
    fig.text(0.01, 0.005,
             "Source: BLS CPI-U. Zero line = overall CPI-U (All Items). Bars show pp above/below.",
             fontsize=8, color=GRAY)

    plt.tight_layout(rect=[0, 0.02, 1, 0.975])
    out = os.path.join(IMG_DIR, "chart2_cpi_categories.png")
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Saved → {out}")

    # Console summary
    beat   = [(c, pct[c]) for c, rv in zip(categories, rel_vals) if rv > 0 and c not in ("All Items", "Wages")]
    lagged = [(c, pct[c]) for c, rv in zip(categories, rel_vals) if rv <= 0 and c not in ("All Items", "Wages")]
    print(f"\n  Overall inflation: {inflation_rate:.1f}%   |   Wage growth: {wage_growth:.1f}%")
    print(f"\n  Categories that OUTPACED inflation ({len(beat)}):")
    for cat, val in sorted(beat, key=lambda x: -x[1]):
        print(f"    {cat:<35} {val:.1f}%  ({val - inflation_rate:+.1f}pp)")
    print(f"\n  Categories that LAGGED inflation ({len(lagged)}):")
    for cat, val in sorted(lagged, key=lambda x: -x[1]):
        print(f"    {cat:<35} {val:.1f}%  ({val - inflation_rate:+.1f}pp)")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("Chart 1: Wages vs CPI (indexed)")
    print("=" * 60)
    chart1_wages_vs_cpi()

    print()
    print("=" * 60)
    print("Chart 2: CPI Categories vs Wage Growth")
    print("=" * 60)
    chart2_cpi_categories()
