# Inflation vs Wages

Python project for analyzing **wages, inflation (CPI), and unemployment** using [FRED](https://fred.stlouisfed.org/) and [BLS](https://www.bls.gov/developers/) data. Produces interactive Plotly charts and summary tables.

**Related:** [Have wages kept up with inflation?](https://www.youtube.com/watch?v=46rAsbFmRBw&t=1s) · [FRED API](https://fred.stlouisfed.org/docs/api/fred/) · [BLS API](https://www.bls.gov/developers/api_signature_v2.htm)

---

## Purpose

The purpose of this project is to get familiarized with the BLS api and run basic visualizations of CPI and wage data.

## Setup

1. **Clone and create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **API keys (required for FRED and BLS):**
   - **Option A (recommended):** Set environment variables:
     - `FRED_API_KEY` — get a key at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
     - `BLS_API_KEY` — get a key at [BLS](https://www.bls.gov/developers/home/registration_key.htm)
   - **Option B:** Copy `src/constants.example.py` to `src/constants.py` and add your keys there. (Do not commit `constants.py`; it is in `.gitignore`.)

Run all commands from the **project root** (the folder that contains `src/` and `data/`).

---

## How to run

| Script | Description |
|--------|-------------|
| **Wages vs inflation** | Indexed nominal wages, CPI, and real wages (FRED). |
| **Unemployment** | Unemployment rate by group from `data/unemployment_data.csv`; plot + % change table. |
| **Employment by sector (CES)** | Nonfarm payrolls by industry from FRED. |
| **Detailed CPI** | BLS CPI by category (food, energy, housing, etc.); CSV + % increase table. |

```bash
# Wages vs inflation (default dates: 2019-01-01 to 2025-12-31)
python src/inflation.py --start_date=2019-04-01 --end_date=2025-12-31

# Unemployment (uses data/unemployment_data.csv)
python src/unemployment.py --start_date=2019-01-01 --end_date=2025-12-31

# Employment by sector (optional: --units=pch for % change)
python src/ces.py --start_date=2019-01-01 --end_date=2024-12-31

# Detailed CPI (BLS; start/end are years)
python src/cpi.py --start_date=2000-01-01 --end_date=2025-12-31
```

---

## Project layout

- **`src/`** — Scripts and shared code (`utilities.py`, `bls_api_2.py`, `constants.example.py`)
- **`data/`** — CSV inputs (e.g. `unemployment_data.csv`, `wage_vs_inflation.csv`)
- **`images/`** — Saved charts (optional)
- **`requirements.txt`** — Python dependencies

Scripts open **interactive Plotly** (or matplotlib) windows; some also write CSVs (e.g. `detailed_cpi_analysis.csv`).
