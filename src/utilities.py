from fredapi import Fred
import pandas as pd
import constants
import argparse
import plotly.graph_objects as go
    
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_date', type=str, default='2019-01-01', help='Start date for the data in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, default='2025-12-31', help='End date for the data in YYYY-MM-DD format')

    return parser.parse_args()  

def fetch_data(series_list, start_date, end_date):
    fred = Fred(api_key=constants.FRED_API_KEY)

    data = pd.DataFrame()
    for series_id, series_name in series_list.items():
        print(f'Fetching data for {series_name} ({series_id})')
        series_data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        data[series_name] = series_data

    data.to_csv('data.csv', index=True)
    
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