from utilities import fetch_bls_series_list, get_args
import pandas as pd
import os
from datetime import date

series_list = {
    'CUUR0000SA0': 'All Items',
    'CUUR0000SAF': 'Food Bev',
    'CUUR0000SAF11': 'Food at Home',
    'CUUR0000SAF111': 'Cereals Bakery',
    'CUUR0000SAF112': 'Meats Poultry Fish Eggs',
    'CUUR0000SAF113': 'Fruits Veg',
    'CUUR0000SAF114': 'Nonalc Bev',
    'CUUR0000SAF115': 'Other Food at Home',
    'CUUR0000SEFJ': 'Dairy',
    'CUUR0000SEFV': 'Food Away Home',
    'CUUR0000SEFV01': 'Full Service Meals',
    'CUUR0000SEFV02': 'Limited Service Meals',
    'CUUR0000SA0E': 'Energy',
    'CUUR0000SETB01': 'Gasoline',
    'CUUR0000SEHF01': 'Electricity',
    'CUUR0000SEHF02': 'Utility Gas',
    'CUUR0000SA0L1E': 'Less Food Energy',
    'CUUR0000SAH': 'Housing',
    'CUUR0000SAH1': 'Shelter',
    'CUUR0000SAA': 'Apparel',
    'CUUR0000SAR': 'Recreation',
    'CUUR0000SAE1': 'Education',
    'CUUR0000SAE2': 'Communication',
    'CUUR0000SAM': 'Medical Care',
    'CUUR0000SEMD01': 'Hospital Services',
    'CUUR0000SEMC01': 'Physicians Services',
    'CUUR0000SEMF01': 'Prescription Drugs',
    'CUUR0000SAT': 'Transportation',
    'CUUR0000SETA01': 'New Vehicles',
    'CUUR0000SETA02': 'Used Cars Trucks',
}

def main():
    args = get_args()

    start_year = args.start_date
    end_year = args.end_date

    print(f"Downloading CPI data from {start_year} to {end_year}...")
    df = fetch_bls_series_list(series_list, start_year, end_year)
    
    if not df.empty:
        output_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prepared_cpi_data.csv')
        df.to_csv(output_file, index=True)
        print(f"Successfully downloaded and saved CPI data to {output_file}")
    else:
        print("No data was returned from the BLS API.")

if __name__ == "__main__":
    main()
