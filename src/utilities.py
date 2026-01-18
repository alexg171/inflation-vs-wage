from fredapi import Fred
import pandas as pd
import constants
import argparse
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
    
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_date', type=str, default='2019-01-01', help='Start date for the data in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, default='2025-12-31', help='End date for the data in YYYY-MM-DD format')
    parser.add_argument('--units', type=str, default=None, help='Units for the data (e.g., lin, chg, ch1, pc1, pca, cch, cca, log)')

    return parser.parse_args()  

def fetch_data(series_list, start_date, end_date, units='lin'):
    fred = Fred(api_key=constants.FRED_API_KEY)

    data = pd.DataFrame()
    for series_id, series_name in series_list.items():
        print(f'Fetching data for {series_name} ({series_id})')
        series_data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date, units=units)
        data[series_name] = series_data
    
    return data

def create_plot(title, yaxis_title, data: pd.DataFrame, start_date, end_date):
    fig = go.Figure()
    for column in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', name=column))

    fig.update_layout(
        title=f'{title} ({start_date} to {end_date})',
        xaxis_title='Date',
        yaxis_title=yaxis_title,
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

def create_simple_plot(title, yaxis_title, data: pd.DataFrame, start_date, end_date):
    plt.figure(figsize=(15, 7))
    for column in data.columns:
        plt.plot(data.index, data[column], label=column)
    
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator()) # Monthly ticks

    plt.title(f'{title} ({start_date} to {end_date})', fontsize=14)
    plt.grid(True, which='both', alpha=0.3)
    plt.axhline(100, color='black', linewidth=1)
    plt.legend()
    plt.tight_layout()
    plt.show()

units = {
    'Levels': 'lin',
    'Change': 'chg',
    'Change from Year Ago': 'ch1',
    'Percent Change': 'pch',
    'Percent Change from Year Ago': 'pc1',
    'Compounded Annual Rate of Change': 'pca',
    'Continuously Compounded Rate of Change': 'cch',
    'Continuously Compounded Annual Rate of Change': 'cca',
    'Natural Log': 'log'
}
