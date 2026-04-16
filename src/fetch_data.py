"""
fetch_data.py — Pull all data needed for both charts from BLS in one run.

Fetches:
  - Average Hourly Earnings (CES0500000003) — wages for Chart 1
  - CPI-U All Items + all subcategories — Charts 1 & 2

Saves to: data/all_data.csv

BLS API limits this script works around automatically:
  - Max 25 series per request  -> splits into series batches
  - Max 20 years per request   -> splits date range into 20-year windows

Append mode (default): loads existing CSV, fetches only dates not yet present,
merges, and saves. Use --full to re-fetch everything from scratch.

Run:
  cd src
  python fetch_data.py                   # append new months to existing data
  python fetch_data.py --full            # re-fetch everything from 1947
  python fetch_data.py --start_year 2000 --full  # re-fetch from custom year
"""

import os
import sys
import argparse
from datetime import date
import pandas as pd
from bls_api_2 import post_multiple_series

# ── Series definitions ─────────────────────────────────────────────────────────
# Wages series starts ~2006; CPI All Items goes back to 1947.
# Series with shorter histories simply return NaN for earlier dates.
WAGES = {"CES0500000003": "Wages"}

CPI_SERIES = {
    "CUUR0000SA0":    "All Items",
    "CUUR0000SAF":    "Food Bev",
    "CUUR0000SAF11":  "Food at Home",
    "CUUR0000SAF111": "Cereals Bakery",
    "CUUR0000SAF112": "Meats Poultry Fish Eggs",
    "CUUR0000SAF113": "Fruits Veg",
    "CUUR0000SAF114": "Nonalc Bev",
    "CUUR0000SAF115": "Other Food at Home",
    "CUUR0000SEFJ":   "Dairy",
    "CUUR0000SEFV":   "Food Away Home",
    "CUUR0000SEFV01": "Full Service Meals",
    "CUUR0000SEFV02": "Limited Service Meals",
    "CUUR0000SA0E":   "Energy",
    "CUUR0000SETB01": "Gasoline",
    "CUUR0000SEHF01": "Electricity",
    "CUUR0000SEHF02": "Utility Gas",
    "CUUR0000SA0L1E": "Less Food Energy",
    "CUUR0000SAH":    "Housing",
    "CUUR0000SAH1":   "Shelter",
    "CUUR0000SAA":    "Apparel",
    "CUUR0000SAR":    "Recreation",
    "CUUR0000SAE1":   "Education",
    "CUUR0000SAE2":   "Communication",
    "CUUR0000SAM":    "Medical Care",
    "CUUR0000SEMD01": "Hospital Services",
    "CUUR0000SEMC01": "Physicians Services",
    "CUUR0000SEMF01": "Prescription Drugs",
    "CUUR0000SAT":    "Transportation",
    "CUUR0000SETA01": "New Vehicles",
    "CUUR0000SETA02": "Used Cars Trucks",
}

EARLIEST_YEAR   = 2006   # wages series (CES0500000003) starts Mar 2006
BLS_BATCH_SIZE  = 25     # max series per BLS API request
BLS_YEAR_WINDOW = 20     # max years per BLS API request

OUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "all_data.csv")


# ── BLS helpers ────────────────────────────────────────────────────────────────

def _parse_bls_response(response, series_map):
    """Convert a BLS API response dict into a DataFrame indexed by Date."""
    if response.get("status") == "REQUEST_FAILED":
        msg = response.get("message", ["Unknown error"])
        raise RuntimeError(f"BLS API request failed: {msg}")

    frames = []
    for series in response["Results"]["series"]:
        sid  = series["seriesID"]
        name = series_map.get(sid, sid)
        rows = series.get("data", [])
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df["Date"] = pd.to_datetime(
            df["year"] + "-" + df["period"].str.replace("M", "", regex=False) + "-01"
        )
        df[name] = pd.to_numeric(df["value"], errors="coerce")
        frames.append(df.set_index("Date")[[name]])

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).sort_index()


def _fetch_with_windows(series_map, start_year, end_year):
    """
    Fetch <=25 series across any date range by splitting into 20-year windows
    and stitching results together.
    """
    windows = []
    y = start_year
    while y <= end_year:
        y_end = min(y + BLS_YEAR_WINDOW - 1, end_year)
        print(f"    [{y}–{y_end}] ", end="", flush=True)
        resp = post_multiple_series(list(series_map.keys()), y, y_end)
        df = _parse_bls_response(resp, series_map)
        if not df.empty:
            windows.append(df)
            print(f"{len(df)} rows")
        else:
            print("no data")
        y = y_end + 1

    if not windows:
        return pd.DataFrame()
    combined = pd.concat(windows)
    combined = combined[~combined.index.duplicated(keep="last")]
    return combined.sort_index()


def _fetch_all_series(start_year, end_year):
    """Fetch all series in batches of 25, each batch spanning the full date range."""
    all_series = {**WAGES, **CPI_SERIES}
    items      = list(all_series.items())
    n_batches  = -(-len(items) // BLS_BATCH_SIZE)
    all_frames = []

    for i in range(0, len(items), BLS_BATCH_SIZE):
        batch     = dict(items[i : i + BLS_BATCH_SIZE])
        batch_num = i // BLS_BATCH_SIZE + 1
        names     = list(batch.values())
        print(f"  Batch {batch_num}/{n_batches}: {names[0]} ... {names[-1]}")
        df = _fetch_with_windows(batch, start_year, end_year)
        if not df.empty:
            all_frames.append(df)
        print()

    if not all_frames:
        return pd.DataFrame()

    result = pd.concat(all_frames, axis=1).sort_index()
    result = result.loc[:, ~result.columns.duplicated()]
    return result


# ── Main ───────────────────────────────────────────────────────────────────────

def fetch_all(start_year, end_year, append=True):
    existing = pd.DataFrame()

    if append and os.path.exists(OUT_CSV):
        existing = pd.read_csv(OUT_CSV, index_col="Date", parse_dates=True)
        last_date = existing.index.max()
        # Start fetching from the year after the last full year we already have
        fetch_start = last_date.year
        print(f"Existing data: {existing.index.min().strftime('%Y-%m')} to "
              f"{last_date.strftime('%Y-%m')} ({len(existing)} rows)")
        print(f"Fetching updates from {fetch_start} to {end_year}...\n")
    else:
        fetch_start = start_year
        print(f"Full fetch: {fetch_start} to {end_year}\n")

    if fetch_start > end_year:
        print("Already up to date.")
        return

    new_data = _fetch_all_series(fetch_start, end_year)

    if new_data.empty:
        print("No new data returned.")
        return

    if not existing.empty:
        # Merge: existing rows take priority for old dates; new rows fill in the rest
        combined = pd.concat([existing, new_data])
        combined = combined[~combined.index.duplicated(keep="last")]
        result = combined.sort_index()
    else:
        result = new_data

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    result.index.name = "Date"
    result.to_csv(OUT_CSV)

    print(f"Saved {len(result)} rows x {len(result.columns)} columns")
    print(f"Date range: {result.index.min().strftime('%Y-%m')} to {result.index.max().strftime('%Y-%m')}")
    print(f"-> {os.path.abspath(OUT_CSV)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch all BLS data for inflation vs wages charts.")
    parser.add_argument("--start_year", type=int, default=EARLIEST_YEAR,
                        help=f"First year to fetch in full mode (default: {EARLIEST_YEAR})")
    parser.add_argument("--end_year", type=int, default=date.today().year,
                        help="Last year to fetch (default: current year)")
    parser.add_argument("--full", action="store_true",
                        help="Re-fetch everything from scratch instead of appending")
    args = parser.parse_args()

    if args.start_year > args.end_year:
        print("Error: start_year must be <= end_year")
        sys.exit(1)

    fetch_all(args.start_year, args.end_year, append=not args.full)
