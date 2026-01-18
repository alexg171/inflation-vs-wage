import requests
import json
import constants

BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
API_KEY = constants.BLS_API_KEY
HEADERS = {'Content-type': 'application/json'}

def get_single_series(series_id):
    """GET request for a single series (last 3 years only)"""
    url = f"{BASE_URL}{series_id}"
    response = requests.get(url)
    return response.json()

def post_multiple_series(series_ids, startyear, endyear):
    """POST request for multiple series (no optional parameters)"""
    payload = {
        "seriesid": series_ids,
        "startyear": str(startyear),
        "endyear": str(endyear),
        "registrationkey": API_KEY
    }
    response = requests.post(BASE_URL, data=json.dumps(payload), headers=HEADERS)
    return response.json()

def post_series_with_options(series_ids, startyear, endyear,
                              catalog=False, calculations=False,
                              annualaverage=False, aspects=False):
    """POST request with optional parameters"""
    payload = {
        "seriesid": series_ids,
        "startyear": str(startyear),
        "endyear": str(endyear),
        "catalog": catalog,
        "calculations": calculations,
        "annualaverage": annualaverage,
        "aspects": aspects,
        "registrationkey": API_KEY
    }
    response = requests.post(BASE_URL, data=json.dumps(payload), headers=HEADERS)
    return response.json()

def get_latest_series(series_id):
    """GET request for the latest data point of a series"""
    url = f"{BASE_URL}{series_id}/latest"
    response = requests.get(url)
    return response.json()

def get_popular_series():
    """GET request for popular series"""
    url = f"{BASE_URL}popular"
    response = requests.get(url)
    return response.json()

def get_all_surveys():
    """GET request for all surveys metadata"""
    url = f"{BASE_URL}surveys"
    response = requests.get(url)
    return response.json()

def get_single_survey(survey_id):
    """GET request for metadata about a single survey"""
    url = f"{BASE_URL}surveys/{survey_id}"
    response = requests.get(url)
    return response.json()