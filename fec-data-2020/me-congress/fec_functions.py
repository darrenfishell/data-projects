import pandas as pd
import requests
import config
import datadotworld as dw
import pygsheets
import http.client
import json
import time
import os
from pandas.io.json import json_normalize

##Schedule_a API guide: https://api.open.fec.gov/developers/#/receipts/get_schedules_schedule_a_˜

#Define functions
def get_cands(state, cycle):
    state = state.split(',')
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/candidates/search'

    for state in state:

        for cycle in cycle:
            params = {'election_year': cycle
                , 'state': state
                , 'api_key': config.fec_key}

            r = requests.get(end, params=params).json()

            cand_all = []
            cands = json_normalize(data=r['results']) \
                [['candidate_id'
                    , 'name'
                    , 'party_full'
                    , 'incumbent_challenge_full'
                    , 'office_full'
                    , 'first_file_date'
                  ]]

            comm = json_normalize(data=r['results'],
                                  record_path='principal_committees') \
                [['candidate_ids'
                    , 'committee_id'
                    , 'name']]

            comm['candidate_ids'] = comm['candidate_ids'].str[0]

            # Merge candidate and committee lookups
            cands = cands.merge(comm, left_on='candidate_id', right_on='candidate_ids')

            # Rename cols
            colnm = {
                'name_x': 'candidate_name'
                , 'name_y': 'committee_name'
            }
            cands.rename(columns=colnm, inplace=True)
            cands.drop(columns='candidate_ids', inplace=True)

            cand_all.append(cands)

    cand_all = pd.concat(cand_all, sort=False, ignore_index=True).drop_duplicates()

    return cand_all


def get_committees(names):
    names = names.split(',')

    comms = []
    end = 'https://api.open.fec.gov/v1/names/committees'

    for name in names:
        params = {'q': name
            , 'api_key': config.fec_key}

        r = requests.get(end, params=params).json()

        comm = json_normalize(data=r['results'])

        comms.append(comm)

    comm_all = pd.concat(comms, sort=False, ignore_index=True).drop_duplicates()

    return comm_all


def get_itemized(cycle, cands):

    def new_unitem(cycle, cands, commid):


        udf = []
        end = 'https://api.open.fec.gov/v1/committee'
        params = {
            'api_key': config.fec_key
            , 'cycle': cycle
            , 'per_page': '100'
        }

        candidate = cands['candidate_name'][idx]
        path = os.path.join(end, commid, 'totals')
        print(path)

        # Collect unitemized contributions
        r = requests.get(os.path.join(end, commid, 'totals'), params=params).json()
        udf = json_normalize(r['results'])
        print(candidate)
        print(udf.head())
        return udf

    def get_unitem(cycle, cand, commid):

        udf=[]
        end = 'https://api.open.fec.gov/v1/committee'

        params = {
            'api_key': config.fec_key
            , 'cycle': cycle
            , 'per_page': '100'
        }

        path = os.path.join(end,commid,'totals')

        # Collect unitemized contributions
        r = requests.get(path, params=params).json()

        try:
            udf = json_normalize(r['results'])
        except:
            print(f'No unitemized contributions for {cand}')

        return udf

    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_a/'
    ids = cands['committee_id']
    dfs = []
    udfs = []
    cand_count = len(cands)

    for idx, commid in enumerate(ids):
        page_count = 0

        params = {
            'per_page': '100'
            , 'sort': 'contribution_receipt_date'
            , 'api_key': config.fec_key
            , 'is_individual': 'true'
            , 'two_year_transaction_period': cycle
            , 'last_index': []
            , 'last_contribution_receipt_date': []
            , 'committee_id': commid
        }

        candidate = cands['candidate_name'][idx]

        udfs.append(new_unitem(cycle, cands, commid))

        try:
            r = requests.get(end, params=params).json()
            while r['pagination']['last_indexes'] is not None:
                page_count += 1

                df = json_normalize(r['results'])
                dfs.append(df)

                last_index = r['pagination']['last_indexes']['last_index']
                last_date = r['pagination']['last_indexes']['last_contribution_receipt_date']

                params.update([('last_index', last_index)
                                  , ('last_contribution_receipt_date', last_date)])

                r = requests.get(end, params=params).json()
        except:
            continue

        print(f'Returned {page_count} itemized pages for {candidate}')

    # After for loop, concatenate all dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')
    # ustore = pd.concat(udfs, sort=False, ignore_index=True).drop_duplicates()

    # Clean dataframe ZIPs
    df['contributor_zip'] = df['contributor_zip'].str[:5]

    # Filter to is_individual and no memoed subtotal
    df = df[(df['is_individual'] == True) | (df['memoed_subtotal'] == False)]

    # Transform unitemized table, based on df structure
    cols = df.columns.values.tolist()
    udf = pd.DataFrame(columns=cols)

    targetcols = ['committee.name'
        , 'committee.party_full'
        , 'committee_id'
        , 'contribution_receipt_amount'
        , 'contribution_receipt_date'
        , 'fec_election_type_desc']

    sourcecols = ['committee_name'
        , 'party_full'
        , 'committee_id'
        , 'individual_unitemized_contributions'
        , 'coverage_end_date'
        , 'last_report_type_full']

    udf[targetcols] = ustore[sourcecols]

    # Add labels
    udf['contributor_name'] = 'Unitemized individual contributions'
    udf['entity_type'] = 'IND'

    # Combine dataframes
    df = pd.concat([df, udf], sort=False, ignore_index=True)

    # Parse datetime
    df['contribution_receipt_date'] = df['contribution_receipt_date'].str.split('T', expand=True)[0]

    return df


def get_ies(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_e/'
    ids = cands['candidate_id']
    dfs = []
    page_count = 0

    for idx, item in enumerate(ids):

        params = {
            'per_page': '100'
            , 'api_key': config.fec_key
            , 'cycle': cycle
            , 'last_index': []
            , 'last_expenditure_date': []
            , 'candidate_id': item
        }

        r = requests.get(end, params=params).json()

        candidate = cands['candidate_name'][idx]

        try:
            while r['pagination']['last_indexes'] is not None:
                df = json_normalize(r['results'])
                dfs.append(df)

                last_index = r['pagination']['last_indexes']['last_index']
                last_date = r['pagination']['last_indexes']['last_expenditure_date']

                params.update([('last_index', last_index)
                                  , ('last_expenditure_date', last_date)])


                r = requests.get(end, params=params).json()

                print(f'IEs failed at page {page_count} of {pages} for {candidate}.')
        except:
            continue

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

    # Clean dataframe
    df['commiteee.zip'] = df['committee.zip'].str[:5]
    df['expenditure_date'] = df['expenditure_date'].str.split('T', expand=True)[0]

    return df


def get_coordinated(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_f/'
    ids = cands['candidate_id']
    dfs = []

    for i, item in enumerate(ids):

        params = {
            'per_page': '100'
            , 'api_key': config.fec_key
            , 'two_year_transaction_period': cycle
            , 'page': 1
            , 'candidate_id': item
        }

        r = requests.get(end, params=params).json()

        current_pg = r['pagination']['page']
        all_pgs = r['pagination']['pages']

        candidate = cands['candidate_name'][i]

        for page in range(all_pgs):
            params.update([('page', page + 1)])
            r = requests.get(end, params=params).json()

            df = json_normalize(r['results'])
            dfs.append(df)

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

    # Clean dataframe
    df['commiteee.zip'] = df['committee.zip'].str[:5]

    return df


def get_summary(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/committee/'
    ids = cands['committee_id']
    dfs = []

    for idx, item in enumerate(ids):
        params = {
            'api_key': config.fec_key
            , 'cycle': cycle
            , 'per_page': '100'
            , 'committee_id': item
        }

        r = requests.get(end + item + '/totals', params=params).json()

        df = json_normalize(r['results'])
        dfs.append(df)

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    return df


def write_cands(df):
    with dw.open_remote_file('darrenfishell/2020-election-repo', 'candidate_committee_lookup.csv') as w:
        df.to_csv(w, index=False)


def write_indiv(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM individual_congressional_contributions')
    test = len(results.dataframe) < len(df)
    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'individual-congressional-contributions.csv') as w:
            df.to_csv(w, index=False)
    return test


def write_summary(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_financial_summaries')
    test = sum(results.dataframe['receipts']) < len(df['receipts'])
    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'congress_financial_summaries.csv') as w:
            df.to_csv(w, index=False)
    return test


def write_ies(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_independent_expenditures')
    test = len(results.dataframe) < len(df)
    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'congress-independent-expenditures.csv') as w:
            df.to_csv(w, index=False)
    return test


def write_coord(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_party_coordinated_expenditures')
    test = len(results.dataframe) < len(df)
    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo',
                                 'congress-party-coordinated-expenditures.csv') as w:
            df.to_csv(w, index=False)
    return test


def write_to_gsheet():
    gc = pygsheets.authorize(service_file='gcreds.json')
    conn = http.client.HTTPSConnection("api.data.world")
    headers = {'authorization': "Bearer " + config.dw_key}

    sheets_to_dw = [['maine-congress-2020', 'e2b1bde2-1e60-4d49-bd31-da5aa7ce0611', 'campaign-summaries'],
                    ['maine-congress-2020', '026e8f40-d10e-4324-8b45-80dbc0e61627', 'individual-contributors']]

    for idx, sheet in enumerate(sheets_to_dw):
        sheet = [x[0] for x in sheets_to_dw][idx]
        queryid = [x[1] for x in sheets_to_dw][idx]
        gsh_name = [x[2] for x in sheets_to_dw][idx]

        # Retrieve query
        conn.request("GET", "/v0/queries/" + queryid, headers=headers)
        data = conn.getresponse().read()
        # Execute Query
        results = dw.query('darrenfishell/2020-election-repo', json.loads(data)['body']).dataframe

        # Prepare to load into Google Sheets
        sh = gc.open(sheet)
        wks = sh.worksheet('title', gsh_name)
        wks.clear()
        wks.rows = results.shape[0]
        wks.set_dataframe(results, start='A1', nan='')