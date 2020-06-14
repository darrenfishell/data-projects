import pandas as pd
import requests
import os
import config
import pygsheets
import http.client
import datadotworld as dw
import json
from io import StringIO
from pandas.io.json import json_normalize


def lambda_handler(event, context):
    # Initialize session
    s = requests.Session()
    cookies = requests.cookies.RequestsCookieJar()

    # URL and session variables
    url_base = config.url_base
    headers = config.headers
    year = config.year

    print(year)

    # Execute queries
    try:
        length = get_cands(year, headers)
        print(f'Wrote records for {length} candidates.')
    except:
        print('Failed to write candidate lookup.')

    # Get candidate contributions
    try:
        get_trans(year, headers)
        print('Contributions loaded')
    except:
        print('Failed to write some file')

    try:
        write_to_gsheet()
        print('Wrote records to GSheet')
    except:
        print("Write to GSheet failed")


# GET CANDS / TRANSACTION FUNCTIONS
def get_cands(year, headers):
    # GET CANDIDATES LOOKUP#
    url = 'https://mainecampaignfinance.com/api///Organization/SearchCandidates'

    data = {"ElectionYear": year,
            "pageNumber": 1,
            "pageSize": 2147483647}

    s = requests.Session()
    cookies = requests.cookies.RequestsCookieJar()

    r = s.post(url, data=json.dumps(data), headers=headers).json()

    df = json_normalize(r)

    length = len(df)

    with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', 'candidate_lookup.csv') as w:
        df.to_csv(w, index=False)

    return length


def get_trans(year, headers):
    url = 'https://mainecampaignfinance.com/api///Search/TransactionSearchInformationExpExportToCSV'

    s = requests.Session()
    cookies = requests.cookies.RequestsCookieJar()

    # Parameters for looping through search
    committee_types = {'candidate': '01'
        , 'bqc': '02'
        , 'pac': '03'
        , 'party-committee': '09'}

    transaction_types = {'contributions': 'CON'
        , 'expenditures': 'EXP'
        , 'independent_expenditures_2': 'IE'}

    trans_types = list(transaction_types.values())
    filenames = list(transaction_types.keys())
    comm_types = list(committee_types.values())

    # Data dictionary for query
    data = {"ElectionYear": year
        , "pageNumber": '1'
        , "pageSize": '2147483647'  # Sets max responses from page (defaults to 10)
        , "ValidationRequired": '0'}

    for idx, b in enumerate(transaction_types):

        data.update({"TransactionType": trans_types[idx]})

        file = filenames[idx]

        dfs = []

        # Reset index

        for i, n in enumerate(comm_types):

            data.update({"CommitteeType": comm_types[i]})

            comm_type = comm_types[i]

            try:
                r = s.post(url, data=json.dumps(data), headers=headers)
                df = pd.read_csv(StringIO(r.content.decode('utf-8')))
                dfs.append(df)
                print(f'Loaded {file} for {comm_type} to dataframe')
            except:
                continue

        # COMBINE dfs
        df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

        length = len(df)
        count = dw.query('darrenfishell/2020-maine-state-campaign-finance', 'SELECT COUNT(*) FROM '+filenames[idx]).dataframe['count'][0]

        print(count)

        if count < len(df):
            with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', file + '.csv') as w:
                df.to_csv(w, index=False)
            print(f'Wrote file {file}.csv to data.world, at {length} records.')
        else:
            print(f'No updates to {file}.')

def write_to_gsheet():
    # Write contribution query to GSheets
    gc = pygsheets.authorize(service_file='gcreds.json')
    conn = http.client.HTTPSConnection("api.data.world")

    headers = {'authorization': "Bearer " + config.dw_key}

    queryid = 'a65bf908-26ba-4f11-b413-a57bd8b3a9f5'
    project = '2020-maine-state-campaign-finance'
    gsh_idx = 0
    sheet = 'maine-state-campaign-finance-2020'

    # Retrieve query
    conn.request("GET", "/v0/queries/" + queryid, headers=headers)
    data = conn.getresponse().read()
    # Execute Query
    results = dw.query('darrenfishell/' + project, json.loads(data)['body']).dataframe

    # Prepare to load into Google Sheets
    sh = gc.open(sheet)
    wks = sh.worksheet('index', gsh_idx)
    wks.clear()
    wks.rows = results.shape[0]
    wks.set_dataframe(results, start='A1', nan='')

event=[]
context=[]
lambda_handler(event, context)