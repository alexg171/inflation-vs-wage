from fredapi import Fred
import pandas as pd
import constants
import argparse
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bls_api_2 import post_multiple_series

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
        data[series_id] = series_data
    
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

def create_simple_plot(title, data: pd.DataFrame, start_date, end_date):
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

def fetch_bls_series_list(series_list, start_date, end_date):
    response_json = post_multiple_series(list(series_list.keys()), start_date, end_date)
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
        return df
    else:
        return pd.DataFrame()

def summarize_cpi_percentage_increase(df):
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

    # Prepare cell colors: highlight 'All Items' row
    cell_colors = []
    for idx, metric in enumerate(summary_df['Metric']):
        if metric == 'All Items':
            cell_colors.append('lightblue')
        else:
            cell_colors.append('white')

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(summary_df.columns),
                    align='left'),
        cells=dict(
            values=[summary_df[col] for col in summary_df.columns],
            align='left',
            fill_color=[cell_colors] * len(summary_df.columns)
        ))
    ])
    fig.update_layout(title=f"CPI Percentage Increase Summary ({valid_series.index.min().year} to {valid_series.index.max().year})")
    fig.show()

def generate_summary_table(df, start_date, end_date):
    summary = []
    for col in ['Nominal Wages', 'Real Wages']:
        start_val = df.loc[start_date, col] if start_date in df.index else df[col].iloc[0]
        end_val = df.loc[end_date, col] if end_date in df.index else df[col].iloc[-1]
        net_change = ((end_val - start_val) / start_val) * 100
        summary.append([
            col.replace('Wages', 'Wage'),
            f"${start_val:.2f}",
            f"${end_val:.2f}",
            f"{net_change:+.1f}%"
        ])
    header = [
        "Metric",
        pd.to_datetime(start_date).strftime('%b %Y'),
        pd.to_datetime(end_date).strftime('%b %Y'),
        "Net Change"
    ]
    fig = go.Figure(data=[go.Table(
        header=dict(values=header, align='left'),
        cells=dict(values=list(zip(*summary)), align='left')
    )])
    fig.update_layout(title="Summary Table: Wages and Inflation")
    fig.show()
    
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
