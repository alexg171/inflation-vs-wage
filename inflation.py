from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import constants
import argparse
    
parser = argparse.ArgumentParser()
parser.add_argument('--start_date', type=str, default='2007-01-01', help='Start date for the data in YYYY-MM-DD format')
parser.add_argument('--end_date', type=str, default='2012-12-31', help='End date for the data in YYYY-MM-DD format')

args = parser.parse_args()  

fred = Fred(api_key=constants.FRED_API_KEY)

start_date=args.start_date
end_date=args.end_date

# Average Hourly Earnings of All Employees, Total Private (CES0500000003)
wages = fred.get_series('CES0500000003', observation_start=start_date, observation_end=end_date)

# Consumer Price Index for All Urban Consumers: All Items in U.S. City Average, Index 1982-1984=100, Seasonally Adjusted (CPIAUCSL)
cpi = fred.get_series('CPIAUCSL', observation_start=start_date, observation_end=end_date)

data = pd.DataFrame({'Wages': wages, 'CPI': cpi})
data.dropna(inplace=True)

data['WAGES_IDX'] = (data['Wages'] / data['Wages'].iloc[0]) * 100
data['CPI_IDX'] = (data['CPI'] / data['CPI'].iloc[0]) * 100
data['Real Wages'] = (data['WAGES_IDX'] / data['CPI_IDX'])*100

plt.figure(figsize=(15, 7))
plt.plot(data.index, data['WAGES_IDX'], label='Nominal Wages', color='blue')
plt.plot(data.index, data['CPI_IDX'], label='CPI', color='red')
plt.plot(data.index, data['Real Wages'], label='Real Wages', color='green')

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.MonthLocator()) # Monthly ticks

plt.title(f'Wage vs Inflation Analysis ({args.start_date} to {args.end_date})', fontsize=14)
plt.grid(True, which='both', alpha=0.3)
plt.axhline(100, color='black', linewidth=1)
plt.legend()
plt.tight_layout()
plt.show()