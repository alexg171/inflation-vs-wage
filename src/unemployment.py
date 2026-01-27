from utilities import get_args, fetch_data, create_plot

series_list = { 
    # overall unemployment rate
    'UNRATE': 'National Avg',

    # # gender
    'LNS14000001': 'Men',
    'LNS14000002': 'Women',

    # # race
    'LNS14000003': 'White',
    'LNS14000006': 'Black or African American',
    'LNS14000009': 'Hispanic or Latino',
    'LNS14032183': 'Asian',

    # # age groups - 16-19
    'LNS14000012': '16-19 Yrs.',
    'LNS14000013': '16-19 Yrs., Men',
    'LNS14000014': '16-19 Yrs., Women',
    'LNS14000015': '16-19 Yrs., White',
    'LNS14000018': '16-19 Yrs., Black or African American',

    # # age groups - 20 and over
    'LNS14000024': '20 Yrs. & over',
    'LNS14000025': '20 Yrs. & over, Men',
    'LNS14000026': '20 Yrs. & over, Women',
    'LNS14000028': '20 Yrs. & over, White Men',
    'LNS14000029': '20 Yrs. & over, White Women',
    'LNS14000031': '20 Yrs. & over, Black or African American Men',

    # # age groups - 20-24
    'LNS14000036': '20-24 Yrs.',
    'LNS14000037': '20-24 Yrs., Men',
    'LNS14000038': '20-24 Yrs., Women',

    # # age groups - 25 and over
    'LNS14000048': '25 Yrs. & over',
    'LNS14000049': '25 Yrs. & over, Men',
    'LNS14000050': '25 Yrs. & over, Women',

    # # age groups - 25-54
    'LNS14000060': '25-54 Yrs.',
    'LNS14000061': '25-54 Yrs., Men',
    'LNS14000062': '25-54 Yrs., Women',

    # # age groups - specific
    'LNS14000086': '16-17 Yrs.',
    'LNS14000088': '18-19 Yrs.',
    'LNS14000089': '25-34 Yrs.',
    'LNS14000091': '35-44 Yrs.',
    'LNS14000093': '45-54 Yrs.',
    'LNS14024230': '55 Yrs. & over',

    # # men
    'LNS14000150': 'Married Men',
    'LNS14000152': '16-17 Yrs., Men',
    'LNS14000154': '18-19 Yrs., Men',
    'LNS14000164': '25-34 Yrs., Men',
    'LNS14000173': '35-44 Yrs., Men',
    'LNS14000182': '45-54 Yrs., Men',
    'LNS14024231': '55 Yrs. & over, Men',

    # # women
    'LNS14000315': 'Married Women',
    'LNS14000317': '16-17 Yrs., Women',
    'LNS14000319': '18-19 Yrs., Women',
    'LNS14000327': '25-34 Yrs., Women',
    'LNS14000334': '35-44 Yrs., Women',
    'LNS14000341': '45-54 Yrs., Women',
    'LNS14024232': '55 Yrs. & over, Women',

    # # other categories
    'LNS14023557': 'Reentrants to Labor Force',
    'LNS14023569': 'New Entrants',
    'LNS14023705': 'Job Leavers',

    # # age groups - 16-24
    'LNS14024885': '16-24 Yrs., Men',
    'LNS14024886': '16-24 Yrs., Women',
    'LNS14024887': '16-24 Yrs.',

    # # education levels
    'LNS14027659': 'Less Than a High School Diploma, 25 Yrs. & over',
    'LNS14027660': 'High School Graduates, No College, 25 Yrs. & over',
    'LNS14027662': 'Bachelor\'s Degree and Higher, 25 Yrs. & over',
    'LNS14027689': 'Some College or Associate Degree, 25 Yrs. & over',
    
    # employment status
    'LNS14100000': 'Unemployment Rate Full-Time Workers',
    'LNS14200000': 'Unemployment Rate Part-Time Workers',

    # # misc
    'PRUR': 'Puerto Rico',
    'U2RATE': 'Job Losers (U-2)',
    'U4RATE': 'Total Unemployed Plus Discouraged Workers, as a Percent of the Civilian Labor Force Plus Discouraged Workers (U-4)',
    'U5RATE': 'Total Unemployed, Plus Discouraged Workers, Plus All Other Persons Marginally Attached to the Labor Force, as a Percent of the Civilian Labor Force Plus All Persons Marginally Attached to the Labor Force (U-5)',
}

args = get_args()

data = fetch_data(series_list, args.start_date, args.end_date)

data.to_csv('unemployment_data.csv', index=True)

# create_plot('Unemployment Rates', 'Percent (%)', data, args.start_date, args.end_date)