import pandas as pd
import requests
import config
import pygsheets
import http.client
import datadotworld as dw
import json
from io import StringIO
from pandas.io.json import json_normalize


def lambda_handler(event, context):
    headers = config.headers
    year = config.year
    bqc_lookup = config.bqcs

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

    try:
        for name, bqc_id in bqc_lookup.items():
            get_bqc(year, name, bqc_id, headers)
            print(f'BQC lookup loaded for {name}')
    except:
        print('BQC committee retrieval failed')

def get_bqc(year, name, bqc_id, headers):
    # GET QUESTION ONE COMMITTEES#
    url = 'https://mainecampaignfinance.com/api///Organization/SearchAssociatedBallotQuestionCommittees'

    s = requests.Session()

    params = {"BallotQuestionTypeId": bqc_id
        , "ElectionYear": year
        , "pageNumber": "1"
        , "pageSize": '10'
        , "sortDir": "desc"
        , "sortedBy": ""}

    r = s.post(url, data=json.dumps(params), headers=headers).json()

    df = json_normalize(r)

    with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', f'{name}-committees.csv') as w:
        df.to_csv(w, index=False)

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
        , 'independent_expenditures': 'IE'}

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

        try:
            count = dw.query('darrenfishell/2020-maine-state-campaign-finance', 'SELECT COUNT(*) FROM '+filenames[idx]).dataframe['count'][0]
        except:
            count = 0

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
    dw_project = '2020-maine-state-campaign-finance'
    sheet = 'maine-state-campaign-finance-2020'
    tab = 'house-and-senate'

    # Retrieve query
    conn.request("GET", "/v0/queries/" + queryid, headers=headers)
    data = conn.getresponse().read()
    # Execute Query
    results = dw.query('darrenfishell/' + dw_project, json.loads(data)['body']).dataframe

    # Prepare to load into Google Sheets
    sh = gc.open(sheet)
    wks = sh.worksheet('title', tab)
    wks.clear()
    wks.rows = results.shape[0]
    wks.set_dataframe(results, start='A1', nan='')
    print(f'Wrote DW {queryid} to GSheets')

event=[]
context=[]
lambda_handler(event, context)