from utilities import *
from bls_api_2 import post_multiple_series

args = get_args()

series_list = {
    # 'CES0500000003': 'Wages',  # Average Hourly Earnings of All Employees, Total Private
    'CPIAUCSL': 'CPI_All_Items',  # Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
    'CUUR0000SA0': 'CPI_All_Items',
    'CUUR0000SAF': 'CPI_Food_Bev',
    'CUUR0000SAF11': 'CPI_Food_at_Home',
    'CUUR0000SAF111': 'CPI_Cereals_Bakery',
    'CUUR0000SAF112': 'CPI_Meats_Poultry_Fish_Eggs',
    'CUUR0000SAF113': 'CPI_Fruits_Veg',
    'CUUR0000SAF114': 'CPI_Nonalc_Bev',
    'CUUR0000SAF115': 'CPI_Other_Food_at_Home',
    'CUUR0000SEFJ': 'CPI_Dairy',
    'CUUR0000SEFV': 'CPI_Food_Away_Home',
    'CUUR0000SEFV01': 'CPI_Full_Service_Meals',
    'CUUR0000SEFV02': 'CPI_Limited_Service_Meals',
    'CUUR0000SA0E': 'CPI_Energy',
    'CUUR0000SETB01': 'CPI_Gasoline',
    'CUUR0000SEHF01': 'CPI_Electricity',
    'CUUR0000SEHF02': 'CPI_Utility_Gas',
    'CUUR0000SA0L1E': 'CPI_Less_Food_Energy',
    'CUUR0000SAH': 'CPI_Housing',
    'CUUR0000SAH1': 'CPI_Shelter',
    'CUUR0000SAA': 'CPI_Apparel',
    'CUUR0000SAR': 'CPI_Recreation',
    'CUUR0000SAE1': 'CPI_Education',
    'CUUR0000SAE2': 'CPI_Communication',
    'CUUR0000SAM': 'CPI_Medical_Care',
    'CUUR0000SEMD01': 'CPI_Hospital_Services',
    'CUUR0000SEMC01': 'CPI_Physicians_Services',
    'CUUR0000SEMF01': 'CPI_Prescription_Drugs',
    'CUUR0000SAT': 'CPI_Transportation',
    'CUUR0000SETA01': 'CPI_New_Vehicles',
    'CUUR0000SETA02': 'CPI_Used_Cars_Trucks',
}

response_json = post_multiple_series(list(series_list.keys()), args.start_date, args.end_date)

all_series_dfs = []

for series in response_json['Results']['series']:
    series_id = series['seriesID']
    readable_name = series_list.get(series_id, series_id)
    data_list = series['data']
    
    if not data_list:
        continue
        
    temp_df = pd.DataFrame(data_list)
    temp_df['Date'] = pd.to_datetime(temp_df['year'] + '-' + temp_df['period'].str.replace('M', '') + '-01')
    temp_df[readable_name] = pd.to_numeric(temp_df['value'], errors='coerce')
    temp_df = temp_df.set_index('Date')[[readable_name]]
    all_series_dfs.append(temp_df)

if all_series_dfs:
    df = pd.concat(all_series_dfs, axis=1)
    df.sort_index(inplace=True)

df.to_csv('detailed_cpi_analysis.csv')
print(df.tail())


summary_data = []

for col in df.columns:
    valid_series = df[col].dropna()
    
    if not valid_series.empty:
        start_year = valid_series.index.min().year
        baseline_date = pd.Timestamp(year=start_year, month=12, day=1)
        
        if baseline_date in valid_series.index:
            start_val = valid_series.loc[baseline_date]
            baseline_dt_str = baseline_date.strftime('%Y-%m-%d')
        else:
            start_val = valid_series.iloc[0]
            baseline_dt_str = valid_series.index[0].strftime('%Y-%m-%d')
            
        end_val = valid_series.iloc[-1]
        end_date_str = valid_series.index[-1].strftime('%Y-%m-%d')

        pct_increase = ((end_val - start_val) / start_val) * 100
        
        summary_data.append({
            'Metric': col,
            'Baseline Date': baseline_dt_str,
            'End Date': end_date_str,
            'Baseline Value': round(float(start_val), 2),
            'End Value': round(float(end_val), 2),
            'Percentage Increase': round(pct_increase, 4)
        })

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.sort_values(by='Percentage Increase', ascending=False)
summary_df.to_csv('cpi_pct_increase_summary.csv', index=False)

print("Summary table created using December baseline.")
print(summary_df.head())

# create_simple_plot('CPI', 'idk yet', df, 2015, 2025)