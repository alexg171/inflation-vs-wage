from utilities import create_plot, get_args, fetch_data

series_list = {
    'PAYEMS': 'Total Nonfarm',
    'USPRIV': 'Total Private',
    'USGOOD': 'Goods-Producing',
    'SRVPRD': 'Service-Providing',
    'CES0800000001': 'Private Service-Providing',
    'USMINE': 'Mining and Logging',
    'USCONS': 'Construction',
    'MANEMP': 'Manufacturing',
    'DMANEMP': 'Durable Goods',
    'NDMANEMP': 'Nondurable Goods',
    'USTPU': 'Trade, Transportation, and Utilities',
    'USWTRADE': 'Wholesale Trade',
    'USTRADE': 'Retail Trade',
    'CES4300000001': 'Transportation and Warehousing',
    'CES4422000001': 'Utilities',
    'USINFO': 'Information',
    'USFIRE': 'Financial Activities',
    'USPBS': 'Professional and Business Services',
    'USEHS': 'Private Education and Health Services',
    'USLAH': 'Leisure and Hospitality',
    'USSERV': 'Other Services',
    'TEMPHELPS': 'Temporary Help Services',
    'USGOVT': 'Government',
}

args = get_args()

data = fetch_data(series_list, args.start_date, args.end_date, args.units)

create_plot('CES', 'Y-Axis Title Here', data, args.start_date, args.end_date)