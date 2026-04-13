import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import argparse
import os

def get_args_for_visualization():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_date', type=str, default='2019-01-01', help='Start date for the data in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, default='2025-12-31', help='End date for the data in YYYY-MM-DD format')
    return parser.parse_args()

def summarize_cpi_percentage_increase(df: pd.DataFrame, start_date=None, end_date=None):
    """
    Generates and displays a Plotly table summarizing the percentage increase
    for each CPI category within the specified date range.
    """
    if start_date:
        df = df.loc[start_date:]
    if end_date:
        df = df.loc[:end_date]

    summary_data = []

    for col in df.columns:
        valid_series = df[col].dropna()
        
        if not valid_series.empty:
            # Determine baseline date for calculation
            calc_start_date = pd.Timestamp(start_date) if start_date else valid_series.index.min()
            calc_end_date = pd.Timestamp(end_date) if end_date else valid_series.index.max()

            # Ensure start_val is taken from the earliest available data point within the range
            # or the beginning of the year of the start_date if available
            start_val_date = valid_series.index.min()
            if start_date:
                start_year_for_baseline = pd.to_datetime(start_date).year
                potential_baseline = pd.Timestamp(year=start_year_for_baseline, month=1, day=1)
                if potential_baseline >= valid_series.index.min() and potential_baseline <= valid_series.index.max():
                    start_val_date = potential_baseline
                elif pd.to_datetime(start_date) >= valid_series.index.min() and pd.to_datetime(start_date) <= valid_series.index.max():
                    start_val_date = pd.to_datetime(start_date)


            # Find the actual value closest to start_val_date
            # Using idxmin() on absolute difference to find closest index
            if not valid_series.empty:
                closest_start_date_idx = (valid_series.index - start_val_date).abs().idxmin()
                start_val = valid_series.loc[closest_start_date_idx]
                actual_baseline_date_str = closest_start_date_idx.strftime('%Y-%m-%d')
            else:
                start_val = None
                actual_baseline_date_str = "N/A"

            # End value is simply the last available value in the filtered series
            end_val = valid_series.iloc[-1]
            end_date_str = valid_series.index[-1].strftime('%Y-%m-%d')

            if start_val is not None:
                pct_increase = ((end_val - start_val) / start_val) * 100
            else:
                pct_increase = float('nan')
            
            summary_data.append({
                'Metric': col,
                'Baseline Date': actual_baseline_date_str,
                'End Date': end_date_str,
                'Baseline Value': round(float(start_val), 2) if start_val is not None else 'N/A',
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
    fig.update_layout(title=f"CPI Percentage Increase Summary ({df.index.min().year} to {df.index.max().year})")
    fig.show()

def create_cpi_plot(title, data: pd.DataFrame, start_date=None, end_date=None):
    """
    Generates and displays a Plotly line plot for CPI data.
    """
    if start_date:
        data = data.loc[start_date:]
    if end_date:
        data = data.loc[:end_date]
        
    fig = go.Figure()
    for column in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', name=column))

    fig.update_layout(
        title=f'{title} ({data.index.min().strftime("%Y-%m-%d")} to {data.index.max().strftime("%Y-%m-%d")})',
        xaxis_title='Date',
        yaxis_title='Index Value',
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


def visualize_cpi_data(df: pd.DataFrame, start_date=None, end_date=None):
    """
    Takes a CPI DataFrame and visualizes it with a plot and a summary table.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Filter data based on provided start_date and end_date if they exist
    if start_date:
        df = df.loc[start_date:]
    if end_date:
        df = df.loc[:end_date]

    if df.empty:
        print("No data available for the specified date range.")
        return

    create_cpi_plot('Categorized CPI', df, start_date, end_date)
    summarize_cpi_percentage_increase(df, start_date, end_date)

if __name__ == "__main__":
    args = get_args_for_visualization()
    _data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    output_file = os.path.join(_data_dir, "prepared_cpi_data.csv")

    if os.path.exists(output_file):
        print(f"Loading CPI data from {output_file}...")
        cpi_df = pd.read_csv(output_file, index_col='Date', parse_dates=True)
        visualize_cpi_data(cpi_df, args.start_date, args.end_date)
    else:
        print(f"Error: {output_file} not found. Please run prepare_cpi_data.py first to generate the data.")
