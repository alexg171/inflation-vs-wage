from utilities import fetch_bls_series_list, get_args, summarize_cpi_percentage_increase, create_simple_plot
import pandas as pd
from datetime import date

series_list = {
    # 'CES0500000003': 'Wages',  # Average Hourly Earnings of All Employees, Total Private
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

args = get_args()

start_year = date(args.start_date).year
end_year = date(args.end_date).year
df = fetch_bls_series_list(series_list, start_year, end_year)

df.to_csv('detailed_cpi_analysis.csv')

summarize_cpi_percentage_increase(df, args.start_date, args.end_date)


# create_simple_plot('Categorized CPI', df, args.start_date, args.end_date)