from utilities import *
    
args = get_args()

series_list = {
    'CES0500000003': 'Wages', #'Average Hourly Earnings of All Employees, Total Private',
    'CPIAUCSL': 'CPI' #'Consumer Price Index for All Urban Consumers: All Items in U.S. City Average',
}

data = fetch_data(series_list, args.start_date, args.end_date)

data.dropna(inplace=True)

idx_data = pd.DataFrame()
idx_data['Nominal Wages'] = (data['Wages'] / data['Wages'].iloc[0]) * 100
idx_data['CPI_IDX'] = (data['CPI'] / data['CPI'].iloc[0]) * 100
idx_data['Real Wages'] = (idx_data['Nominal Wages'] / idx_data['CPI_IDX'])*100

# idx_data.to_csv('wages_inflation_data.csv', index=True)

# generate_summary_table(idx_data, args.start_date, args.end_date)

create_plot('Wages vs Inflation', 'Index (Start Date = 100)', idx_data, args.start_date, args.end_date)
# create_simple_plot('Real Wages Over Time', idx_data, args.start_date, args.end_date)