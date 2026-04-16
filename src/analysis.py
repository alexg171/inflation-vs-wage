"""
analysis.py — Generates the interactive HTML for GitHub Pages.

Run:
  cd src
  python analysis.py

Requires data/all_data.csv — run fetch_data.py first if missing.
"""

import json
import os
import pandas as pd
import plotly.graph_objects as go

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
DOCS_DIR = os.path.join(ROOT, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

ALL_CSV = os.path.join(DATA_DIR, "all_data.csv")

# ── style ──────────────────────────────────────────────────────────────────────
BLUE  = "#2563EB"
RED   = "#DC2626"
GREEN = "#16A34A"
GRAY  = "#6B7280"

# Jan 2019 = 100 baseline for the initial chart render
BASE_DATE = "2019-01-01"

# ── data loading ───────────────────────────────────────────────────────────────

def _load_all_data():
    if not os.path.exists(ALL_CSV):
        raise FileNotFoundError(f"{ALL_CSV} not found. Run fetch_data.py first.")
    df = pd.read_csv(ALL_CSV, index_col="Date", parse_dates=True)
    df = df[df.index >= "2006-01-01"].dropna(subset=["Wages", "All Items"])
    base = df.index[df.index.get_indexer([pd.Timestamp(BASE_DATE)], method="nearest")[0]]
    df["WAGES_IDX"]  = df["Wages"]     / df.loc[base, "Wages"]     * 100
    df["CPI_IDX"]    = df["All Items"] / df.loc[base, "All Items"] * 100
    df["Real Wages"] = df["WAGES_IDX"] / df["CPI_IDX"] * 100
    return df


def _cpi_cols(df):
    return [c for c in df.columns if c not in ("Wages", "WAGES_IDX", "CPI_IDX", "Real Wages")]


# ── chart builders ─────────────────────────────────────────────────────────────

def chart1_plotly(df):
    peak_date = df["CPI_IDX"].idxmax()
    peak_val  = df.loc[peak_date, "CPI_IDX"]
    last      = df.index[-1]

    annotations = [
        dict(text="Source: BLS — Average Hourly Earnings (CES0500000003) & CPI-U (CPIAUCSL). Jan 2019 = 100.",
             xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
             font=dict(size=9, color=GRAY), align="left"),
        dict(x=peak_date, y=peak_val, xref="x", yref="y",
             text=f"Inflation peak<br>{peak_date.strftime('%b %Y')}",
             showarrow=True, arrowhead=2, arrowcolor=RED, ax=-80, ay=-30,
             font=dict(color=RED, size=11)),
    ]
    for val, color, label in [
        (df.loc[last, "WAGES_IDX"],  BLUE,  f"+{df.loc[last, 'WAGES_IDX']-100:.1f}%"),
        (df.loc[last, "CPI_IDX"],    RED,   f"+{df.loc[last, 'CPI_IDX']-100:.1f}%"),
        (df.loc[last, "Real Wages"], GREEN, f"{df.loc[last, 'Real Wages']-100:+.1f}%"),
    ]:
        annotations.append(dict(x=last, y=val, xref="x", yref="y", text=label,
                                showarrow=False, xanchor="left", xshift=6,
                                font=dict(color=color, size=11, family="monospace")))

    fig = go.Figure([
        go.Scatter(x=df.index, y=df["WAGES_IDX"], name="Nominal Wages",
                   line=dict(color=BLUE, width=2.5)),
        go.Scatter(x=df.index, y=df["CPI_IDX"], name="CPI (Inflation)",
                   line=dict(color=RED, width=2.5)),
        go.Scatter(x=df.index, y=df["Real Wages"], name="Real Wages",
                   line=dict(color=GREEN, width=2.5, dash="dash")),
    ])
    fig.add_hline(y=100, line=dict(color=GRAY, width=1, dash="dot"))
    fig.update_layout(
        title=dict(text="Have Wages Kept Up With Inflation?", font=dict(size=18)),
        yaxis_title="Index (Jan 2019 = 100)",
        height=700, legend=dict(x=0.01, y=0.99),
        template="plotly_white", margin=dict(r=70),
        xaxis=dict(
            range=[BASE_DATE, last.strftime("%Y-%m-%d")],
            rangeselector=dict(buttons=[
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=3, label="3y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ]),
            rangeslider=dict(visible=True), type="date",
        ),
        annotations=annotations,
    )
    return fig


def chart2_plotly(df):
    cols = _cpi_cols(df)
    pct = {}
    for col in cols:
        s = df[col].dropna()
        if len(s) >= 2:
            pct[col] = (s.iloc[-1] / s.iloc[0] - 1) * 100
    w = df["Wages"].dropna()
    pct["Wages"] = (w.iloc[-1] / w.iloc[0] - 1) * 100

    inflation_rate = pct.get("All Items", 0)
    wage_growth    = pct["Wages"]
    pct_series = pd.Series(pct).sort_values(ascending=True)
    rel_vals   = pct_series - inflation_rate

    bar_colors = []
    for c, rv in zip(pct_series.index, rel_vals):
        if c == "All Items": bar_colors.append(GRAY)
        elif c == "Wages":   bar_colors.append(BLUE)
        elif rv > 0:         bar_colors.append("#EF4444")
        else:                bar_colors.append("#16A34A")

    start, end = df.index.min(), df.index.max()
    fig = go.Figure(go.Bar(
        x=pct_series.values.tolist(), y=pct_series.index.tolist(),
        orientation="h", marker_color=bar_colors, opacity=0.85,
        text=[f"{v:.1f}%" for v in pct_series.values],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=inflation_rate, line=dict(color=GRAY, width=2, dash="dash"),
                  annotation_text=f"Overall inflation {inflation_rate:.1f}%",
                  annotation_position="top right", annotation_font_color=GRAY)
    fig.add_vline(x=wage_growth, line=dict(color=BLUE, width=2, dash="dash"),
                  annotation_text=f"Wage growth {wage_growth:.1f}%",
                  annotation_position="top left", annotation_font_color=BLUE)
    fig.update_layout(
        title=dict(text=f"Price Change by Category vs. Overall Inflation<br>"
                        f"<sup>{start.strftime('%b %Y')} – {end.strftime('%b %Y')}</sup>",
                   font=dict(size=16)),
        xaxis=dict(title="% Change", ticksuffix="%"),
        template="plotly_white",
        height=max(600, len(pct_series) * 22),
        margin=dict(l=180, r=80, t=80, b=60),
        annotations=[dict(text="Source: BLS CPI-U.", xref="paper", yref="paper",
                          x=0, y=-0.06, showarrow=False,
                          font=dict(size=9, color=GRAY), align="left")],
    )
    return fig


def _build_raw_json(df):
    cols = _cpi_cols(df)
    w = df["Wages"].dropna()
    c1 = {
        "dates": w.index.strftime("%Y-%m-%d").tolist(),
        "wages": w.round(4).tolist(),
        "cpi":   df.loc[w.index, "All Items"].round(4).tolist(),
    }
    c2 = {
        "dates":  df.index.strftime("%Y-%m-%d").tolist(),
        "series": {col: [round(v, 4) if pd.notna(v) else None for v in df[col]]
                   for col in cols},
    }
    return json.dumps({"chart1": c1, "chart2": c2}, separators=(",", ":"))


# ── export ─────────────────────────────────────────────────────────────────────

def export_github_pages():
    df = _load_all_data()

    div1 = chart1_plotly(df).to_html(full_html=False, include_plotlyjs="cdn", div_id="chart1")
    div2 = chart2_plotly(df).to_html(full_html=False, include_plotlyjs=False,  div_id="chart2")

    raw_json = _build_raw_json(df)
    data_min = df.index.min().strftime("%Y-%m")
    data_max = df.index.max().strftime("%Y-%m")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Inflation vs Wages</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem;
      color: #111827; background: #fff;
    }}
    h1 {{ font-size: 2rem; margin-bottom: 0.25rem; }}
    p.subtitle {{ color: #6B7280; margin-top: 0; margin-bottom: 2rem; }}
    h2 {{ font-size: 1.2rem; margin: 2.5rem 0 0.5rem; color: #374151; }}
    hr {{ border: none; border-top: 1px solid #E5E7EB; margin: 2rem 0; }}
    footer {{ margin-top: 3rem; font-size: 0.8rem; color: #9CA3AF; }}
    footer a {{ color: #9CA3AF; }}
    .date-controls {{
      display: flex; align-items: center; gap: 1rem;
      margin-bottom: 1.5rem; flex-wrap: wrap;
      padding: 0.75rem 1rem; background: #F9FAFB;
      border: 1px solid #E5E7EB; border-radius: 8px;
    }}
    .date-controls label {{ font-size: 0.875rem; font-weight: 500; color: #374151; }}
    .date-controls input[type="month"] {{
      font-size: 0.875rem; padding: 0.3rem 0.5rem;
      border: 1px solid #D1D5DB; border-radius: 6px;
      color: #111827; background: #fff;
    }}
    .date-controls span {{ font-size: 0.875rem; color: #6B7280; }}
  </style>
</head>
<body>
  <h1>Inflation vs Wages</h1>
  <p class="subtitle">Interactive charts — data from FRED &amp; BLS</p>

  <div class="date-controls">
    <label for="startMonth">From</label>
    <input type="month" id="startMonth" min="{data_min}" max="{data_max}" value="2019-01" />
    <span>&rarr;</span>
    <label for="endMonth">To</label>
    <input type="month" id="endMonth" min="{data_min}" max="{data_max}" value="{data_max}" />
    <span style="color:#9CA3AF;font-size:0.8rem;">Data as of {data_max}</span>
  </div>

  <h2>Chart 1 &mdash; Have Wages Kept Up With Inflation?</h2>
  {div1}

  <hr />

  <h2>Chart 2 &mdash; Price Change by Category vs. Overall Inflation</h2>
  <div class="date-controls">
    <label for="startMonth2">From</label>
    <input type="month" id="startMonth2" min="{data_min}" max="{data_max}" value="2019-01" />
    <span>&rarr;</span>
    <label for="endMonth2">To</label>
    <input type="month" id="endMonth2" min="{data_min}" max="{data_max}" value="{data_max}" />
    <span style="color:#9CA3AF;font-size:0.8rem;">Data as of {data_max}</span>
  </div>
  {div2}

  <footer>
    Source: <a href="https://www.bls.gov/developers/">BLS API v2</a>.
    Charts built with <a href="https://plotly.com/python/">Plotly</a>.
  </footer>

  <script>
  const RAW  = {raw_json};
  const BLUE = "#2563EB", RED = "#DC2626", GREEN = "#16A34A", GRAY = "#6B7280";

  function filterRange(dates, start, end) {{
    const s = start + "-01", e = end + "-31";
    const idxs = [];
    dates.forEach((d, i) => {{ if (d >= s && d <= e) idxs.push(i); }});
    return idxs;
  }}

  function updateChart1(start, end) {{
    const {{ dates, wages, cpi }} = RAW.chart1;
    const idxs = filterRange(dates, start, end);
    if (idxs.length < 2) return;

    const wageBase = wages[idxs[0]], cpiBase = cpi[idxs[0]];
    const xs   = idxs.map(i => dates[i]);
    const wIdx = idxs.map(i => wages[i] / wageBase * 100);
    const cIdx = idxs.map(i => cpi[i]   / cpiBase  * 100);
    const rIdx = wIdx.map((w, j) => w / cIdx[j] * 100);

    const baseLabel = new Date(xs[0] + "T00:00:00").toLocaleString("en-US", {{month:"short", year:"numeric"}});

    let peakJ = 0;
    cIdx.forEach((v, j) => {{ if (v > cIdx[peakJ]) peakJ = j; }});

    const last = xs.length - 1;

    Plotly.react("chart1", [
      {{ x: xs, y: wIdx, name: "Nominal Wages", type: "scatter", line: {{ color: BLUE, width: 2.5 }} }},
      {{ x: xs, y: cIdx, name: "CPI (Inflation)", type: "scatter", line: {{ color: RED,  width: 2.5 }} }},
      {{ x: xs, y: rIdx, name: "Real Wages",      type: "scatter", line: {{ color: GREEN, width: 2.5, dash: "dash" }} }},
    ], {{
      height: 700, template: "plotly_white",
      title: {{ text: "Have Wages Kept Up With Inflation?", font: {{ size: 18 }} }},
      yaxis: {{ title: {{ text: `Index (${{baseLabel}} = 100)` }} }},
      legend: {{ x: 0.01, y: 0.99 }}, margin: {{ r: 70 }},
      shapes: [{{ type:"line", x0:0, x1:1, xref:"x domain", y0:100, y1:100,
                  line:{{ color:GRAY, width:1, dash:"dot" }} }}],
      xaxis: {{ type:"date", rangeslider:{{ visible:true }},
        rangeselector:{{ buttons:[
          {{ count:1, label:"1y", step:"year", stepmode:"backward" }},
          {{ count:3, label:"3y", step:"year", stepmode:"backward" }},
          {{ label:"All", step:"all" }},
        ]}},
      }},
      annotations: [
        {{ x:xs[peakJ], y:cIdx[peakJ], xref:"x", yref:"y",
           text:`Inflation peak<br>${{xs[peakJ].slice(0,7)}}`,
           showarrow:true, arrowhead:2, arrowcolor:RED, ax:-80, ay:-30,
           font:{{ color:RED, size:11 }} }},
        {{ text:"Source: BLS — Average Hourly Earnings (CES0500000003) & CPI-U (CPIAUCSL).",
           xref:"paper", yref:"paper", x:0, y:-0.12, showarrow:false,
           font:{{ size:9, color:GRAY }}, align:"left" }},
        {{ x:xs[last], y:wIdx[last], xref:"x", yref:"y",
           text:`${{wIdx[last]-100>=0?"+":""}}${{(wIdx[last]-100).toFixed(1)}}%`,
           showarrow:false, xanchor:"left", xshift:6, font:{{ color:BLUE,  size:11, family:"monospace" }} }},
        {{ x:xs[last], y:cIdx[last], xref:"x", yref:"y",
           text:`+${{(cIdx[last]-100).toFixed(1)}}%`,
           showarrow:false, xanchor:"left", xshift:6, font:{{ color:RED,   size:11, family:"monospace" }} }},
        {{ x:xs[last], y:rIdx[last], xref:"x", yref:"y",
           text:`${{rIdx[last]-100>=0?"+":""}}${{(rIdx[last]-100).toFixed(1)}}%`,
           showarrow:false, xanchor:"left", xshift:6, font:{{ color:GREEN, size:11, family:"monospace" }} }},
      ],
    }}, {{ responsive: true }});
  }}

  function updateChart2(start, end) {{
    const {{ dates, series }} = RAW.chart2;
    const idxs = filterRange(dates, start, end);
    if (idxs.length < 2) return;

    const pct = {{}};
    for (const [cat, vals] of Object.entries(series)) {{
      const sv = vals[idxs[0]], ev = vals[idxs[idxs.length-1]];
      if (sv != null && ev != null && sv !== 0) pct[cat] = (ev - sv) / sv * 100;
    }}

    const wDates = RAW.chart1.dates, wages = RAW.chart1.wages;
    const wIdxs = filterRange(wDates, start, end);
    if (wIdxs.length >= 2)
      pct["Wages"] = (wages[wIdxs[wIdxs.length-1]] - wages[wIdxs[0]]) / wages[wIdxs[0]] * 100;

    const inflationRate = pct["All Items"] ?? 0;
    const wageGrowth   = pct["Wages"] ?? 0;
    const sorted = Object.entries(pct).sort((a, b) => a[1] - b[1]);
    const cats = sorted.map(([k]) => k);
    const vals = sorted.map(([, v]) => v);
    const colors = cats.map((c, i) =>
      c === "All Items" ? GRAY : c === "Wages" ? BLUE : vals[i] > inflationRate ? "#EF4444" : "#16A34A"
    );

    const startLabel = new Date(start + "-01T00:00:00").toLocaleString("en-US", {{month:"short", year:"numeric"}});
    const endLabel   = new Date(end   + "-01T00:00:00").toLocaleString("en-US", {{month:"short", year:"numeric"}});

    Plotly.react("chart2", [{{
      x: vals, y: cats, type: "bar", orientation: "h",
      marker: {{ color: colors }}, opacity: 0.85,
      text: vals.map(v => `${{v.toFixed(1)}}%`), textposition: "outside",
      hovertemplate: "%{{y}}: %{{x:.1f}}%<extra></extra>",
    }}], {{
      height: Math.max(600, cats.length * 22),
      template: "plotly_white",
      title: {{ text:`Price Change by Category vs. Overall Inflation<br><sup>${{startLabel}} – ${{endLabel}}</sup>`, font:{{ size:16 }} }},
      xaxis: {{ title:{{ text:"% Change" }}, ticksuffix:"%" }},
      margin: {{ l:180, r:80, t:80, b:60 }},
      shapes: [
        {{ type:"line", x0:inflationRate, x1:inflationRate, xref:"x", y0:0, y1:1, yref:"y domain", line:{{ color:GRAY, width:2, dash:"dash" }} }},
        {{ type:"line", x0:wageGrowth,    x1:wageGrowth,    xref:"x", y0:0, y1:1, yref:"y domain", line:{{ color:BLUE, width:2, dash:"dash" }} }},
      ],
      annotations: [{{ text:"Source: BLS CPI-U.", xref:"paper", yref:"paper",
        x:0, y:-0.06, showarrow:false, font:{{size:9,color:GRAY}}, align:"left", xanchor:"left", yanchor:"top" }}],
    }}, {{ responsive: true }});
  }}

  function syncAndUpdate(sourceId) {{
    const pairedId = sourceId === "startMonth"  ? "startMonth2"
                   : sourceId === "startMonth2" ? "startMonth"
                   : sourceId === "endMonth"    ? "endMonth2"
                   :                              "endMonth";
    document.getElementById(pairedId).value = document.getElementById(sourceId).value;
    const start = document.getElementById("startMonth").value;
    const end   = document.getElementById("endMonth").value;
    if (start && end && start <= end) {{
      updateChart1(start, end);
      updateChart2(start, end);
    }}
  }}

  ["startMonth","endMonth","startMonth2","endMonth2"].forEach(id =>
    document.getElementById(id).addEventListener("change", () => syncAndUpdate(id))
  );

  // Initialize on load
  updateChart1("2019-01", "{data_max}");
  updateChart2("2019-01", "{data_max}");
  </script>
</body>
</html>"""

    out = os.path.join(DOCS_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    export_github_pages()
