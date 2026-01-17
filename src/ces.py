from utilities import create_plot, get_args, fetch_data
from bls_api_2 import post_multiple_series


series_list = {
    'MANEMP': 'All Employees, Manufacturing',
    'NDMANEMP': 'All Employees, Nondurable Goods',
    'PAYEMS': 'All Employees, Total Nonfarm',
    'SRVPRD': 'All Employees, Service-Providing',
    'TEMPHELPS': 'All Employees, Temporary Help Services',
    'USCONS': 'All Employees, Construction',
    'USEHS': 'All Employees, Private Education and Health Services',
    'USFIRE': 'All Employees, Financial Activities',
    'USGOOD': 'All Employees, Goods-Producing',
    'USGOVT': 'All Employees, Government',
    'USINFO': 'All Employees, Information',
    'USLAH': 'All Employees, Leisure and Hospitality',
    'USMINE': 'All Employees, Mining and Logging',
    'USPBS': 'All Employees, Professional and Business Services',
    'USPRIV': 'All Employees, Total Private',
    'USSERV': 'All Employees, Other Services',
    'USTPU': 'All Employees, Trade, Transportation, and Utilities',
    'USTRADE': 'All Employees, Retail Trade',
    'USWTRADE': 'All Employees, Wholesale Trade',
}

args = get_args()

data = fetch_data(series_list, args.start_date, args.end_date)

create_plot('CES', 'Y-Axis Title Here', data, args.start_date, args.end_date)