# Inflation vs Wages

Python project for analyzing **wages and inflation (CPI)** using data from [FRED](https://fred.stlouisfed.org/) and [BLS](https://www.bls.gov/developers/).

**Purpose:** Get familiarized with the BLS API and run basic visualizations of CPI and wage data.

**Related:** [Have wages kept up with inflation?](https://www.youtube.com/watch?v=46rAsbFmRBw&t=1s) · [FRED API](https://fred.stlouisfed.org/docs/api/fred/) · [BLS API](https://www.bls.gov/developers/api_signature_v2.htm)

---

## Interactive charts

- **GitHub Pages:** [alexg171.github.io/inflation-vs-wage](https://alexg171.github.io/inflation-vs-wage)
- **Streamlit:** deploy via [streamlit.io](https://streamlit.io) (see below)

---

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **API keys** (required to fetch new data):
   - **Option A (recommended):** Set environment variables `FRED_API_KEY` and `BLS_API_KEY`.
     - Get a FRED key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)
     - Get a BLS key at [bls.gov](https://www.bls.gov/developers/home/registration_key.htm)
   - **Option B:** Copy `src/constants.example.py` → `src/constants.py` and add your keys. (`constants.py` is gitignored.)

---

## How to run

### Generate charts (static PNGs + interactive HTML)

Run from the **project root**:

```bash
python src/analysis.py
```

Outputs:
- `images/chart1_wages_vs_cpi.png` and `images/chart2_cpi_categories.png` — static images
- `docs/chart1_wages_vs_cpi.html` and `docs/chart2_cpi_categories.html` — interactive Plotly charts

### Fetch fresh CPI data

```bash
python src/prepare_cpi_data.py --start_date 2019 --end_date 2026
```

Saves to `data/prepared_cpi_data.csv`.

### Run the Streamlit app locally

```bash
streamlit run streamlit_app.py
```

---

## Deploy

### GitHub Pages

1. Run `python src/analysis.py` to generate `docs/`.
2. Commit and push.
3. In your repo settings → **Pages** → set source to **Deploy from branch**, branch `main`, folder `/docs`.
4. Your charts will be live at `https://<your-username>.github.io/inflation-vs-wage/`.

### Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo.
3. Set **Main file path** to `streamlit_app.py`.
4. Add `FRED_API_KEY` and `BLS_API_KEY` under **Advanced settings → Secrets**.

---

## Project layout

```
src/
  analysis.py          # generates charts (PNGs + HTML)
  prepare_cpi_data.py  # fetches CPI data from BLS API
  utilities.py         # shared helpers (FRED fetch, plotting)
  bls_api_2.py         # BLS API v2 wrapper
  constants.example.py # API key template
data/
  wage_vs_inflation.csv
  prepared_cpi_data.csv
docs/                  # GitHub Pages output (generated)
images/                # Static PNG output (generated)
streamlit_app.py       # Streamlit web app
requirements.txt
```
