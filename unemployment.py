from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import constants
import argparse
    
parser = argparse.ArgumentParser()
parser.add_argument('--start_date', type=str, default='2019-01-01', help='Start date for the data in YYYY-MM-DD format')
parser.add_argument('--end_date', type=str, default='2025-12-31', help='End date for the data in YYYY-MM-DD format')

args = parser.parse_args()  

fred = Fred(api_key=constants.FRED_API_KEY)

start_date=args.start_date
end_date=args.end_date

series_list = {
    # overall unemployment rate
    'UNRATE': 'Unemployment Rate',

    # # gender
    # 'LNS14000001': 'Unemployment Rate - Men',
    # 'LNS14000002': 'Unemployment Rate - Women',

    # race
    'LNS14000003': 'Unemployment Rate - White',
    'LNS14000006': 'Unemployment Rate - Black or African American',
    'LNS14000009': 'Unemployment Rate - Hispanic or Latino',
    'LNS14032183': 'Unemployment Rate - Asian',

    # # age groups - 16-19
    # 'LNS14000012': 'Unemployment Rate - 16-19 Yrs.',
    # 'LNS14000013': 'Unemployment Rate - 16-19 Yrs., Men',
    # 'LNS14000014': 'Unemployment Rate - 16-19 Yrs., Women',
    # 'LNS14000015': 'Unemployment Rate - 16-19 Yrs., White',
    # 'LNS14000018': 'Unemployment Rate - 16-19 Yrs., Black or African American',

    # # age groups - 20 and over
    # 'LNS14000024': 'Unemployment Rate - 20 Yrs. & over',
    # 'LNS14000025': 'Unemployment Rate - 20 Yrs. & over, Men',
    # 'LNS14000026': 'Unemployment Rate - 20 Yrs. & over, Women',
    # 'LNS14000028': 'Unemployment Rate - 20 Yrs. & over, White Men',
    # 'LNS14000029': 'Unemployment Rate - 20 Yrs. & over, White Women',
    # 'LNS14000031': 'Unemployment Rate - 20 Yrs. & over, Black or African American Men',

    # # age groups - 20-24
    # 'LNS14000036': 'Unemployment Rate - 20-24 Yrs.',
    # 'LNS14000037': 'Unemployment Rate - 20-24 Yrs., Men',
    # 'LNS14000038': 'Unemployment Rate - 20-24 Yrs., Women',

    # # age groups - 25 and over
    # 'LNS14000048': 'Unemployment Rate - 25 Yrs. & over',
    # 'LNS14000049': 'Unemployment Rate - 25 Yrs. & over, Men',
    # 'LNS14000050': 'Unemployment Rate - 25 Yrs. & over, Women',

    # # age groups - 25-54
    # 'LNS14000060': 'Unemployment Rate - 25-54 Yrs.',
    # 'LNS14000061': 'Unemployment Rate - 25-54 Yrs., Men',
    # 'LNS14000062': 'Unemployment Rate - 25-54 Yrs., Women',

    # # other specific groups
    # 'LNS14000086': 'Unemployment Rate - 16-17 Yrs.',
    # 'LNS14000088': 'Unemployment Rate - 18-19 Yrs.',
    # 'LNS14000089': 'Unemployment Rate - 25-34 Yrs.',
    # 'LNS14000091': 'Unemployment Rate - 35-44 Yrs.',
    # 'LNS14000093': 'Unemployment Rate - 45-54 Yrs.',

    # # men
    # 'LNS14000150': 'Unemployment Rate - Married Men',
    # 'LNS14000152': 'Unemployment Rate - 16-17 Yrs., Men',
    # 'LNS14000154': 'Unemployment Rate - 18-19 Yrs., Men',
    # 'LNS14000164': 'Unemployment Rate - 25-34 Yrs., Men',
    # 'LNS14000173': 'Unemployment Rate - 35-44 Yrs., Men',
    # 'LNS14000182': 'Unemployment Rate - 45-54 Yrs., Men',

    # # women
    # 'LNS14000315': 'Unemployment Rate - Married Women',
    # 'LNS14000317': 'Unemployment Rate - 16-17 Yrs., Women',
    # 'LNS14000319': 'Unemployment Rate - 18-19 Yrs., Women',
    # 'LNS14000327': 'Unemployment Rate - 25-34 Yrs., Women',
    # 'LNS14000334': 'Unemployment Rate - 35-44 Yrs., Women',
    # 'LNS14000341': 'Unemployment Rate - 45-54 Yrs., Women',

    # # other categories
    # 'LNS14023557': 'Unemployment Rate - Reentrants to Labor Force',
    # 'LNS14023569': 'Unemployment Rate - New Entrants',
    # 'LNS14023705': 'Unemployment Rate - Job Leavers',

    # # age groups - 55 and over
    # 'LNS14024230': 'Unemployment Rate - 55 Yrs. & over',
    # 'LNS14024231': 'Unemployment Rate - 55 Yrs. & over, Men',
    # 'LNS14024232': 'Unemployment Rate - 55 Yrs. & over, Women',

    # # age groups - 16-24
    # 'LNS14024885': 'Unemployment Rate - 16-24 Yrs., Men',
    # 'LNS14024886': 'Unemployment Rate - 16-24 Yrs., Women',
    # 'LNS14024887': 'Unemployment Rate - 16-24 Yrs.',

    # # education levels
    # 'LNS14027659': 'Unemployment Rate - Less Than a High School Diploma, 25 Yrs. & over',
    # 'LNS14027660': 'Unemployment Rate - High School Graduates, No College, 25 Yrs. & over',
    # 'LNS14027662': 'Unemployment Rate - Bachelor\'s Degree and Higher, 25 Yrs. & over',
    # 'LNS14027689': 'Unemployment Rate - Some College or Associate Degree, 25 Yrs. & over',
    
    # # employment status
    # 'LNS14100000': 'Unemployment Rate Full-Time Workers',
    # 'LNS14200000': 'Unemployment Rate Part-Time Workers',

    # # misc
    # 'PRUR': 'Unemployment Rate in Puerto Rico',
    # 'U2RATE': 'Unemployment Rate - Job Losers (U-2)',
    # 'U4RATE': 'Total Unemployed Plus Discouraged Workers, as a Percent of the Civilian Labor Force Plus Discouraged Workers (U-4)',
    # 'U5RATE': 'Total Unemployed, Plus Discouraged Workers, Plus All Other Persons Marginally Attached to the Labor Force, as a Percent of the Civilian Labor Force Plus All Persons Marginally Attached to the Labor Force (U-5)',
}

data = pd.DataFrame()
for series_id, series_name in series_list.items():
    series_data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
    data[series_name] = series_data

data.to_csv('unemployment_rates.csv', index=True)

# plt.figure(figsize=(15, 7))
# for column in data.columns:
#         plt.plot(data.index, data[column], label=column)

# ax = plt.gca()
# ax.xaxis.set_major_locator(mdates.YearLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
# ax.xaxis.set_minor_locator(mdates.MonthLocator()) # Monthly ticks

# plt.title(f'Unemployment Rate ({args.start_date} to {args.end_date})', fontsize=14)
# plt.grid(True, which='both', alpha=0.3)
# plt.axhline(100, color='black', linewidth=1)
# plt.legend()
# plt.tight_layout()
# plt.show()

import plotly.graph_objects as go

fig = go.Figure()
for column in data.columns:
    fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', name=column))

fig.update_layout(
    title=f'Unemployment Rate ({args.start_date} to {args.end_date})',
    xaxis_title='Date',
    yaxis_title='Unemployment Rate (%)',
    legend_title='Series',
    template='plotly_white',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=3, label="3y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

fig.show()